"""Focused tests for asset permission and state-transition contracts."""

from django.test import SimpleTestCase

from growthtwin.modules.assets.contracts import (
    AssetPermissions,
    AssetState,
    AssetWorkflow,
    AssetWorkflowError,
    SecurityScanResult,
)


class AssetWorkflowContractTests(SimpleTestCase):
    def setUp(self):
        self.permissions = AssetPermissions(
            rights_declared=True,
            task_processing_allowed=True,
        )

    def clean_for_extraction(self, *, provider_transfer_allowed=False):
        permissions = AssetPermissions(
            rights_declared=True,
            task_processing_allowed=True,
            provider_transfer_allowed=provider_transfer_allowed,
        )
        return (
            AssetWorkflow()
            .quarantine(permissions)
            .begin_security_scan()
            .record_security_scan(SecurityScanResult.CLEAN)
        )

    def test_permissions_are_required_before_quarantine(self):
        cases = (
            AssetPermissions(),
            AssetPermissions(rights_declared=True),
            AssetPermissions(task_processing_allowed=True),
        )
        for permissions in cases:
            with self.subTest(permissions=permissions):
                with self.assertRaises(AssetWorkflowError):
                    AssetWorkflow().quarantine(permissions)

    def test_only_clean_scan_allows_extraction(self):
        quarantined = AssetWorkflow().quarantine(self.permissions)
        pending = quarantined.begin_security_scan()

        clean = pending.record_security_scan(SecurityScanResult.CLEAN)

        self.assertEqual(clean.state, AssetState.EXTRACTION_PENDING)
        self.assertEqual(clean.scan_result, SecurityScanResult.CLEAN)

    def test_unsafe_scan_is_rejected_and_scan_error_fails_closed(self):
        pending = AssetWorkflow().quarantine(self.permissions).begin_security_scan()

        unsafe = pending.record_security_scan(SecurityScanResult.UNSAFE)
        failed = pending.record_security_scan(SecurityScanResult.ERROR)

        self.assertEqual(unsafe.state, AssetState.REJECTED)
        self.assertEqual(failed.state, AssetState.FAILED)
        with self.assertRaises(AssetWorkflowError):
            unsafe.complete_extraction(succeeded=True)

    def test_extraction_can_complete_only_after_clean_scan(self):
        ready = self.clean_for_extraction().complete_extraction(succeeded=True)
        failed = self.clean_for_extraction().complete_extraction(succeeded=False)

        self.assertEqual(ready.state, AssetState.READY)
        self.assertEqual(failed.state, AssetState.FAILED)

    def test_provider_transfer_permission_is_separate_and_explicit(self):
        no_provider_permission = self.clean_for_extraction().complete_extraction(
            succeeded=True
        )
        with_provider_permission = self.clean_for_extraction(
            provider_transfer_allowed=True
        ).complete_extraction(succeeded=True)

        self.assertFalse(no_provider_permission.provider_processing_allowed)
        self.assertTrue(with_provider_permission.provider_processing_allowed)
        self.assertFalse(
            self.clean_for_extraction(
                provider_transfer_allowed=True
            ).provider_processing_allowed
        )

    def test_provider_permission_cannot_replace_task_permission(self):
        permissions = AssetPermissions(
            rights_declared=True,
            provider_transfer_allowed=True,
        )

        with self.assertRaises(AssetWorkflowError):
            AssetWorkflow().quarantine(permissions)

    def test_processing_state_cannot_be_constructed_without_clean_scan(self):
        permissions = self.permissions

        with self.assertRaises(AssetWorkflowError):
            AssetWorkflow(
                state=AssetState.READY,
                permissions=permissions,
            )

    def test_deletion_requires_request_and_cannot_repeat_after_completion(self):
        workflow = AssetWorkflow()
        with self.assertRaises(AssetWorkflowError):
            workflow.complete_deletion()

        deleted = workflow.request_deletion().complete_deletion()

        self.assertEqual(deleted.state, AssetState.DELETED)
        with self.assertRaises(AssetWorkflowError):
            deleted.request_deletion()
