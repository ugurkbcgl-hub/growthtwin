"""Pure state and permission contracts for future asset handling.

This module has no storage, parser, file, network, or provider integration. It
models transitions only so synthetic callers can reason about fail-closed rules.
"""

from dataclasses import dataclass, replace
from enum import StrEnum


class AssetWorkflowError(ValueError):
    """Raised when an asset action is not permitted by its current state."""


class AssetState(StrEnum):
    AWAITING_DECLARATIONS = "awaiting_declarations"
    QUARANTINED = "quarantined"
    SCAN_PENDING = "scan_pending"
    EXTRACTION_PENDING = "extraction_pending"
    READY = "ready"
    REJECTED = "rejected"
    FAILED = "failed"
    DELETION_REQUESTED = "deletion_requested"
    DELETED = "deleted"


class SecurityScanResult(StrEnum):
    CLEAN = "clean"
    UNSAFE = "unsafe"
    ERROR = "error"


@dataclass(frozen=True)
class AssetPermissions:
    """Separate user declarations; none is inferred from the others."""

    rights_declared: bool = False
    task_processing_allowed: bool = False
    provider_transfer_allowed: bool = False


@dataclass(frozen=True)
class AssetWorkflow:
    """An immutable, non-persistent view of one asset's processing state."""

    state: AssetState = AssetState.AWAITING_DECLARATIONS
    permissions: AssetPermissions = AssetPermissions()
    scan_result: SecurityScanResult | None = None

    def __post_init__(self) -> None:
        processing_states = {
            AssetState.QUARANTINED,
            AssetState.SCAN_PENDING,
            AssetState.EXTRACTION_PENDING,
            AssetState.READY,
        }
        if self.state in processing_states and not (
            self.permissions.rights_declared
            and self.permissions.task_processing_allowed
        ):
            raise AssetWorkflowError(
                "Processing states require rights and task permission."
            )
        if self.state in {AssetState.EXTRACTION_PENDING, AssetState.READY} and (
            self.scan_result is not SecurityScanResult.CLEAN
        ):
            raise AssetWorkflowError("Extraction requires a recorded clean scan.")
        if self.state is AssetState.REJECTED and (
            self.scan_result is not SecurityScanResult.UNSAFE
        ):
            raise AssetWorkflowError("Rejected state requires an unsafe scan result.")

    @property
    def provider_processing_allowed(self) -> bool:
        """Whether a later provider adapter could process this ready asset."""

        return (
            self.state is AssetState.READY
            and self.scan_result is SecurityScanResult.CLEAN
            and self.permissions.task_processing_allowed
            and self.permissions.provider_transfer_allowed
        )

    def quarantine(self, permissions: AssetPermissions) -> "AssetWorkflow":
        """Mark declarations accepted; this contract writes no file to quarantine."""

        self._require_state(AssetState.AWAITING_DECLARATIONS)
        if not permissions.rights_declared or not permissions.task_processing_allowed:
            raise AssetWorkflowError(
                "Rights declaration and task-specific permission are required."
            )
        return replace(self, state=AssetState.QUARANTINED, permissions=permissions)

    def begin_security_scan(self) -> "AssetWorkflow":
        """Start a future scan after quarantine; this method performs no scan."""

        self._require_state(AssetState.QUARANTINED)
        return replace(self, state=AssetState.SCAN_PENDING)

    def record_security_scan(
        self, result: SecurityScanResult
    ) -> "AssetWorkflow":
        """Advance only clean scans to extraction; errors fail closed."""

        self._require_state(AssetState.SCAN_PENDING)
        next_state = {
            SecurityScanResult.CLEAN: AssetState.EXTRACTION_PENDING,
            SecurityScanResult.UNSAFE: AssetState.REJECTED,
            SecurityScanResult.ERROR: AssetState.FAILED,
        }[result]
        return replace(self, state=next_state, scan_result=result)

    def complete_extraction(self, *, succeeded: bool) -> "AssetWorkflow":
        """Record an extraction outcome without storing extracted content."""

        self._require_state(AssetState.EXTRACTION_PENDING)
        if self.scan_result is not SecurityScanResult.CLEAN:
            raise AssetWorkflowError("Extraction requires a recorded clean scan.")
        next_state = AssetState.READY if succeeded else AssetState.FAILED
        return replace(self, state=next_state)

    def request_deletion(self) -> "AssetWorkflow":
        """Begin deletion from any state except one already marked deleted."""

        self._require_state_not(AssetState.DELETED)
        return replace(self, state=AssetState.DELETION_REQUESTED)

    def complete_deletion(self) -> "AssetWorkflow":
        """Record completion after a future adapter removes every derivative."""

        self._require_state(AssetState.DELETION_REQUESTED)
        return replace(self, state=AssetState.DELETED)

    def _require_state(self, expected: AssetState) -> None:
        if self.state is not expected:
            raise AssetWorkflowError(
                f"Action requires {expected.value}; current state is "
                f"{self.state.value}."
            )

    def _require_state_not(self, forbidden: AssetState) -> None:
        if self.state is forbidden:
            raise AssetWorkflowError(
                f"Action is not permitted from {forbidden.value}."
            )
