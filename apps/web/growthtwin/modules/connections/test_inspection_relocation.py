"""Pure relocation admission; no private source, file or database is opened."""

from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase

from scripts import prepare_recovered_inspection as preparation


class InspectionRepositoryRelocationTests(TestCase):
    def setUp(self):
        self.current = Path(preparation.__file__).resolve().parents[3]
        self.relative = Path(
            "apps/web/growthtwin/modules/connections/migrations/0007_candidate_inspection_permit.py"
        )
        self.legacy = Path(r"C:\Users\Public\Desktop\GrowthTwin")

    def helper(self, repository):
        return SimpleNamespace(
            REPO=repository,
            MIGRATION=repository / self.relative,
            DB="fabricated-private-db-binding",
            AUDIT="fabricated-audit-binding",
            ROOT="fabricated-preparation-binding",
            POINTER="fabricated-backup-pointer-binding",
            AUDIT_SHA="fabricated-audit-source-pin",
        )

    def test_known_legacy_root_rebinds_only_repository_and_migration(self):
        helper = self.helper(self.legacy)
        before = vars(helper).copy()
        result = preparation._bind_repository(helper)
        self.assertIs(result, helper)
        self.assertEqual(helper.REPO, self.current)
        self.assertEqual(helper.MIGRATION, self.current / self.relative)
        for field, value in before.items():
            if field not in ("REPO", "MIGRATION"):
                self.assertEqual(getattr(helper, field), value)

    def test_current_root_is_accepted_without_other_changes(self):
        helper = self.helper(self.current)
        before = vars(helper).copy()
        self.assertIs(preparation._bind_repository(helper), helper)
        self.assertEqual(vars(helper), before)

    def test_unknown_root_refuses_without_mutation(self):
        helper = self.helper(self.current / "fabricated-unrecognized-checkout")
        before = vars(helper).copy()
        with self.assertRaisesRegex(ValueError, "Repository scope changed"):
            preparation._bind_repository(helper)
        self.assertEqual(vars(helper), before)

    def test_wrong_migration_refuses_both_accepted_roots_without_mutation(self):
        for repository in (self.legacy, self.current):
            with self.subTest(repository=repository):
                helper = self.helper(repository)
                helper.MIGRATION = repository / "fabricated-other-migration.py"
                before = vars(helper).copy()
                with self.assertRaises(ValueError):
                    preparation._bind_repository(helper)
                self.assertEqual(vars(helper), before)

    def test_cross_bound_migration_refuses_without_mutation(self):
        helper = self.helper(self.legacy)
        helper.MIGRATION = self.current / self.relative
        if self.current == self.legacy:
            self.skipTest("This checkout is the original legacy location.")
        before = vars(helper).copy()
        with self.assertRaises(ValueError):
            preparation._bind_repository(helper)
        self.assertEqual(vars(helper), before)

    def test_string_or_missing_repository_binding_is_not_admitted(self):
        helpers = (
            SimpleNamespace(
                REPO=str(self.legacy), MIGRATION=str(self.legacy / self.relative)
            ),
            SimpleNamespace(MIGRATION=self.current / self.relative),
        )
        for helper in helpers:
            with self.subTest(helper_type=type(helper)), self.assertRaises(ValueError):
                preparation._bind_repository(helper)
