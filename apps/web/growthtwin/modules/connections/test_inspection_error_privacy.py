"""Real Django traceback filtering with fabricated values and mocked boundaries."""

from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.test import SimpleTestCase, override_settings
from django.views.debug import SafeExceptionReporterFilter

from . import backend
from . import candidate_inspection_recovery as recovery
from . import candidate_recovered_readback as readback
from . import scoped_oauth_candidate as candidate
from .connector_identity import IdentityConflict


@override_settings(DEBUG=False)
class InspectionErrorPrivacyTests(SimpleTestCase):
    def setUp(self):
        self.session = "fabricated-inspection-report-session"
        self.values = dict(
            owner=SimpleNamespace(pk=107),
            workspace_id=214,
            connection_id=uuid4(),
            attempt_id=uuid4(),
            request_id=uuid4(),
            session_key=self.session,
        )
        self.report_filter = SafeExceptionReporterFilter()

    def assert_masked_frames(self, call, expected):
        """Inspect product frames, not the test driver that supplies test inputs."""
        try:
            call()
        except Exception as error:
            found = set()
            traceback = error.__traceback__
            while traceback is not None:
                frame = traceback.tb_frame
                key = (frame.f_globals.get("__name__"), frame.f_code.co_name)
                if key in expected:
                    sensitive_name = expected[key]
                    self.assertIn(sensitive_name, frame.f_locals)
                    filtered = dict(
                        self.report_filter.get_traceback_frame_variables(None, frame)
                    )
                    self.assertEqual(
                        filtered[sensitive_name], self.report_filter.cleansed_substitute
                    )
                    self.assertNotIn(self.session, repr(filtered))
                    found.add(key)
                traceback = traceback.tb_next
            self.assertEqual(found, set(expected))
        else:
            self.fail("The fabricated failure did not reach the expected frames.")

    def test_direct_reader_helpers_mask_raw_session_dictionary(self):
        unavailable = IdentityConflict("Fabricated scope unavailable.")
        with (
            patch.object(readback, "_enabled"),
            patch.object(readback.transaction, "atomic", side_effect=nullcontext),
            patch.object(recovery, "_scope", side_effect=unavailable),
        ):
            self.assert_masked_frames(
                lambda: readback._checked(self.values),
                {(readback.__name__, "_checked"): "values"},
            )
        with patch.object(readback.storage, "_locations", side_effect=unavailable):
            self.assert_masked_frames(
                lambda: readback._locations(self.values, SimpleNamespace()),
                {(readback.__name__, "_locations"): "values"},
            )
            with patch.object(readback, "_enabled"):
                self.assert_masked_frames(
                    lambda: readback._unchanged_locations(
                        self.values, SimpleNamespace(), object()
                    ),
                    {
                        (readback.__name__, "_unchanged_locations"): "values",
                        (readback.__name__, "_locations"): "values",
                    },
                )

    def test_direct_recovery_apis_mask_raw_session_argument(self):
        with patch.object(
            recovery, "salted_hmac", side_effect=RuntimeError("Fabricated failure.")
        ):
            self.assert_masked_frames(
                lambda: recovery._session(self.session),
                {(recovery.__name__, "_session"): "session_key"},
            )
        with patch.object(
            recovery, "_gate", side_effect=IdentityConflict("Fabricated denial.")
        ):
            self.assert_masked_frames(
                lambda: recovery.consume_inspection_permit(**self.values),
                {(recovery.__name__, "consume_inspection_permit"): "session_key"},
            )
            self.assert_masked_frames(
                lambda: recovery.issue_inspection_permit(
                    **self.values,
                    expected_generation=uuid4(),
                    expected_revision=0,
                    expected_receipt_key="0" * 64,
                    recovery_confirmation=True,
                ),
                {(recovery.__name__, "issue_inspection_permit"): "session_key"},
            )

    def test_direct_origin_session_and_legacy_binding_helpers_are_masked(self):
        with patch.object(
            candidate, "salted_hmac", side_effect=RuntimeError("Fabricated failure.")
        ):
            self.assert_masked_frames(
                lambda: candidate._session_key(self.session),
                {(candidate.__name__, "_session_key"): "session_key"},
            )
        with override_settings(
            GOOGLE_ADS_LOCAL_OWNER_ID=107, GOOGLE_ADS_LOCAL_WORKSPACE_ID=214
        ):
            self.assert_masked_frames(
                lambda: backend._token_path(("foreign-owner", "214", self.session)),
                {(backend.__name__, "_token_path"): "binding"},
            )

    def test_reader_entry_and_nested_error_frames_are_filtered(self):
        with (
            patch.object(readback, "_enabled"),
            patch.object(recovery, "_gate"),
            patch.object(readback.transaction, "atomic", side_effect=nullcontext),
            patch.object(
                recovery, "_scope", side_effect=IdentityConflict("Fabricated denial.")
            ),
        ):
            self.assert_masked_frames(
                lambda: readback.inspect_recovered_candidate(**self.values),
                {
                    (readback.__name__, "inspect_recovered_candidate"): "session_key",
                    (readback.__name__, "_checked"): "values",
                },
            )
