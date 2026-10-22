"""No-I/O candidate recovery assessment using fabricated receipts only."""

from datetime import timedelta
from uuid import uuid4

from django.test import TransactionTestCase, override_settings
from django.utils import timezone

from . import candidate_recovery as recovery
from . import test_scoped_oauth_candidate as fixtures
from .connector_identity import IdentityConflict
from .models import ScopedOAuthCandidateAttempt as Attempt


@override_settings(GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=True)
class CandidateRecoveryTests(fixtures.CandidateFixture, TransactionTestCase):
    def assess(self, **changes):
        values = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            attempt_id=self.attempt_id,
            session_key=self.session,
        )
        before = list(Attempt.objects.values())
        counts = [
            mock.call_count
            for mock in (
                self._client,
                self._post,
                self._read,
                self._write,
                self._token_path,
            )
        ]
        result = recovery.assess_candidate(**(values | changes))
        self.assertEqual(
            counts,
            [
                mock.call_count
                for mock in (
                    self._client,
                    self._post,
                    self._read,
                    self._write,
                    self._token_path,
                )
            ],
        )
        self.assertEqual(list(Attempt.objects.values()), before)
        self.assertFalse(result.can_retry_exchange)
        self.assertFalse(result.can_activate)
        self.assertNotIn("fabricated", repr(result))
        return result

    def test_reserved_wait_is_not_permission_and_lost_session_requires_review(self):
        self.begin()
        self.assertEqual(self.assess().disposition, "callback_wait")
        result = self.assess(session_key=None)
        self.assertEqual(result.disposition, "restart_review")
        self.assertFalse(result.session_matches)
        self.assertEqual(self.assess(session_key="other").disposition, "restart_review")

    def test_expired_reserved_requires_review_without_retiring_it(self):
        self.begin()
        old = timezone.now() - timedelta(minutes=6)
        Attempt.objects.update(created_at=old, expires_at=old + timedelta(minutes=5))
        self.assertEqual(self.assess().disposition, "restart_review")
        self.assertEqual(Attempt.objects.get().state, "reserved")

    def test_uncertainty_survives_session_loss_and_expiry(self):
        self.begin()
        old = timezone.now() - timedelta(days=1)
        Attempt.objects.update(created_at=old, expires_at=old + timedelta(minutes=5))
        for state, reason in (("exchanging", ""), ("uncertain", "storage_uncertain")):
            Attempt.objects.update(state=state, reason=reason)
            self.assertEqual(
                self.assess(session_key=None).disposition, "reconciliation_required"
            )

    def test_block_does_not_downgrade_uncertainty(self):
        self.begin()
        Attempt.objects.update(state="uncertain", reason="exchange_uncertain")
        self.block()
        result = self.assess(session_key=None)
        self.assertEqual(result.disposition, "reconciliation_required")
        self.assertFalse(result.current_scope)

    def test_rotation_does_not_downgrade_uncertainty(self):
        self.begin()
        Attempt.objects.update(state="exchanging")
        self.rotate()
        result = self.assess()
        self.assertEqual(result.disposition, "reconciliation_required")
        self.assertFalse(result.current_scope)

    def test_candidate_stays_inactive_and_rejected_stays_history(self):
        self.prepare()
        self.consume()
        old = timezone.now() - timedelta(days=1)
        Attempt.objects.update(created_at=old, expires_at=old + timedelta(minutes=5))
        self.assertEqual(
            self.assess(session_key=None).disposition, "inactive_candidate_review"
        )
        Attempt.objects.update(state="rejected", reason="callback_invalid")
        self.assertEqual(self.assess().disposition, "rejected_history")

    def test_metadata_assessment_available_with_adapter_off(self):
        self.begin()
        with override_settings(GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=False):
            self.assertEqual(self.assess().disposition, "callback_wait")

    def test_unknown_and_corrupt_receipts_fail_closed(self):
        self.begin()
        with self.assertRaises(Attempt.DoesNotExist):
            self.assess(attempt_id=uuid4())
        Attempt.objects.update(reason="storage_uncertain")
        with self.assertRaises(IdentityConflict):
            self.assess()
