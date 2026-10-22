"""Synthetic operator-session rehearsal and fabricated read-only-plan checks."""

import copy
import json
import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.db import transaction
from django.test import SimpleTestCase, TransactionTestCase, override_settings
from django.utils import timezone

from growthtwin.modules.workspaces.models import Workspace
from scripts import prepare_recovered_inspection as launcher


@override_settings(DEBUG=False)
class SyntheticOperatorSessionTests(TransactionTestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username="fabricated-inspection-owner", password=None
        )
        self.workspace = Workspace.objects.create(
            owner=self.owner, name="Fabricated inspection workspace"
        )
        self.config = override_settings(
            GOOGLE_ADS_LOCAL_OWNER_ID=str(self.owner.pk),
            GOOGLE_ADS_LOCAL_WORKSPACE_ID=str(self.workspace.pk),
        )
        self.config.enable()
        self.addCleanup(self.config.disable)

    def binding(self):
        return launcher._owned_synthetic_session(
            owner=self.owner, workspace_id=self.workspace.pk
        )

    def test_fresh_server_session_reloads_exact_owner_and_cleans_only_itself(self):
        before = list(get_user_model().objects.values())
        with self.binding() as (authenticated, key):
            self.assertEqual(authenticated.pk, self.owner.pk)
            self.assertTrue(authenticated.is_authenticated)
            self.assertFalse(authenticated.has_usable_password())
            self.assertEqual(len(key), 32)
            row = Session.objects.get(session_key=key)
            self.assertGreater(row.expire_date, timezone.now())
            self.assertLessEqual(
                (row.expire_date - timezone.now()).total_seconds(), 300
            )
            self.assertEqual(row.get_decoded()["_auth_user_id"], str(self.owner.pk))
        self.assertFalse(Session.objects.exists())
        self.assertEqual(list(get_user_model().objects.values()), before)

    def test_body_failure_still_cleans_session_without_rewriting_password(self):
        before = self.owner.password
        with self.assertRaisesRegex(RuntimeError, "Fabricated failure"):
            with self.binding():
                raise RuntimeError("Fabricated failure")
        self.assertFalse(Session.objects.exists())
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.password, before)

    def test_preexisting_session_refuses_without_deleting_it(self):
        existing = SessionStore()
        existing["fixture"] = "retained"
        existing.create()
        with self.assertRaises(ValueError):
            with self.binding():
                self.fail("Existing session must refuse admission")
        self.assertEqual(
            list(Session.objects.values_list("session_key", flat=True)),
            [existing.session_key],
        )

    def test_usable_password_or_wrong_scope_refuses_before_creating_session(self):
        self.owner.set_password("fabricated-only-not-a-user-credential")
        self.owner.save(update_fields=["password"])
        with self.assertRaises(ValueError):
            with self.binding():
                self.fail("Usable password must refuse synthetic bootstrap")
        self.owner.set_unusable_password()
        self.owner.save(update_fields=["password"])
        with override_settings(GOOGLE_ADS_LOCAL_WORKSPACE_ID="wrong-fixture"):
            with self.assertRaises(ValueError):
                with self.binding():
                    self.fail("Wrong scope must refuse")
        self.assertFalse(Session.objects.exists())

    def test_caller_transaction_refuses(self):
        with transaction.atomic(), self.assertRaises(ValueError):
            with self.binding():
                self.fail("Caller transaction must refuse")
        self.assertFalse(Session.objects.exists())

    def test_failed_reload_removes_only_the_minted_session(self):
        with patch("django.contrib.auth.get_user", side_effect=ValueError):
            with self.assertRaises(ValueError):
                with self.binding():
                    self.fail("Invalid reload must refuse")
        self.assertFalse(Session.objects.exists())

    def test_create_failure_after_insert_still_cleans_matching_minted_session(self):
        original = SessionStore.create

        def failed_create(store):
            original(store)
            raise RuntimeError("Fabricated post-insert failure")

        with patch.object(SessionStore, "create", failed_create):
            with self.assertRaisesRegex(RuntimeError, "post-insert failure"):
                with self.binding():
                    self.fail("Creation failure must not yield a binding")
        self.assertFalse(Session.objects.exists())

    def test_concurrently_added_other_session_is_retained_for_review(self):
        other = SessionStore()
        with self.assertRaisesRegex(ValueError, "cleanup requires review"):
            with self.binding():
                other["fixture"] = "retained-other-session"
                other.create()
        self.assertEqual(
            list(Session.objects.values_list("session_key", flat=True)),
            [other.session_key],
        )

    def test_changed_minted_session_is_not_deleted_by_cleanup(self):
        key = None
        with self.assertRaisesRegex(ValueError, "cleanup requires review"):
            with self.binding() as (_, key):
                store = SessionStore(session_key=key)
                store["inspection_nonce"] = "fabricated-changed-binding"
                store.save()
        self.assertTrue(Session.objects.filter(session_key=key).exists())

    def test_auth_field_change_with_same_nonce_is_retained_for_review(self):
        key = None
        with self.assertRaisesRegex(ValueError, "cleanup requires review"):
            with self.binding() as (_, key):
                store = SessionStore(session_key=key)
                store["_auth_user_backend"] = "fabricated-changed-backend"
                store.save()
        self.assertTrue(Session.objects.filter(session_key=key).exists())

    def test_encoded_row_drift_during_reload_never_yields_binding(self):
        minted = []

        def changed_reload(request):
            key = request.session.session_key
            minted.append(key)
            changed = SessionStore(session_key=key)
            changed["fabricated_extra"] = "changed-after-insertion"
            changed.save()
            return self.owner

        with patch("django.contrib.auth.get_user", side_effect=changed_reload):
            with self.assertRaises(ValueError):
                with self.binding():
                    self.fail("Changed row must not yield a binding")
        self.assertEqual(len(minted), 1)
        self.assertTrue(Session.objects.filter(session_key=minted[0]).exists())


class FabricatedPlanTests(SimpleTestCase):
    def setUp(self):
        appdata = Path(tempfile.gettempdir()) / "fabricated-no-files-appdata"
        self.env = patch.dict(os.environ, {"LOCALAPPDATA": str(appdata)})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.root = appdata / "Temp/gwt-inspection-schema-backup-fabricated"
        self.before = {
            "schema": [["table", "old", "old", "CREATE TABLE old(id)"]],
            "data": {"old": "fabricated-fingerprint"},
            "migrations": [["connections", "0006_candidate_retirement_binding"]],
            "permit_count": None,
        }
        self.after = copy.deepcopy(self.before)
        self.after["schema"].append(
            ["table", launcher.NEW_TABLE, launcher.NEW_TABLE, "fabricated-sql"]
        )
        self.after["migrations"].append(list(launcher.TARGET))
        self.after["permit_count"] = 0
        self.manifest = {
            "version": 1,
            "before": copy.deepcopy(self.before),
            "plan": [[*launcher.TARGET, False]],
            **dict.fromkeys(
                ("backup_hash", "audit_hash", "migration_hash", "preparation_hash"),
                "fabricated-hash",
            ),
        }
        self.helper = SimpleNamespace(
            AUDIT=appdata / "fabricated-audit.py",
            ROOT=appdata / "fabricated-preparation",
            DB=appdata / "fabricated.sqlite3",
            MIGRATION=appdata / "fabricated-migration.py",
            POINTER=appdata / "fabricated-pointer.json",
            load_audit=Mock(
                return_value=SimpleNamespace(
                    no_reparse=Mock(), private_acls=Mock(return_value=True)
                )
            ),
            admission=Mock(),
            read_json=Mock(
                side_effect=lambda _, path: (
                    {"version": 1, "backup_root": str(self.root)}
                    if path.name == "fabricated-pointer.json"
                    else self.manifest
                )
            ),
            hash_file=Mock(return_value="fabricated-hash"),
            hash_value=lambda value: json.dumps(value, sort_keys=True),
            snapshot=Mock(
                side_effect=lambda _, path, **kwargs: (
                    self.before if path.name == "before-0007.sqlite3" else self.after
                )
            ),
        )

    def run_plan(self):
        with patch.object(launcher, "_load_preparation", return_value=self.helper):
            return launcher._plan()

    def test_plan_reports_no_execution_or_current_client_proof(self):
        result = self.run_plan()
        self.assertTrue(result["read_only_admission"])
        self.assertFalse(result["execution_available"])
        self.assertFalse(result["current_client_hash_proved"])
        self.assertFalse(result["credential_contents_read"])
        self.helper.admission.assert_called_once_with(
            self.helper.load_audit.return_value, migrated=True
        )

    def test_changed_history_data_permit_or_migration_plan_refuses(self):
        cases = (
            lambda: self.after["data"].update(old="changed"),
            lambda: self.after.update(permit_count=1),
            lambda: self.after["migrations"].append(["connections", "unexpected"]),
            lambda: self.manifest.update(plan=[]),
        )
        baseline_after = copy.deepcopy(self.after)
        baseline_manifest = copy.deepcopy(self.manifest)
        for mutate in cases:
            with self.subTest(case=mutate):
                self.after = copy.deepcopy(baseline_after)
                self.manifest = copy.deepcopy(baseline_manifest)
                mutate()
                with self.assertRaises(ValueError):
                    self.run_plan()

    def test_unavailable_private_acl_refuses(self):
        self.helper.load_audit.return_value.private_acls.return_value = False
        with self.assertRaises(ValueError):
            self.run_plan()
