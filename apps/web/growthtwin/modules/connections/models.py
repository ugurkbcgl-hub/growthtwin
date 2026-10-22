"""Connector identity and isolated closure metadata; never credentials or content."""

from uuid import uuid4

from django.db import models
from django.utils import timezone


class SyntheticConnectionScope(models.Model):
    """Positive fixture registration, not an actual Google grant/connection."""

    class State(models.TextChoices):
        QUARANTINED = "quarantined"
        OPEN = "open"
        BLOCKED = "blocked"

    id = models.UUIDField(primary_key=True, editable=False)
    workspace = models.ForeignKey("workspaces.Workspace", on_delete=models.PROTECT)
    generation = models.UUIDField(editable=False)
    state = models.CharField(max_length=16, choices=State, default=State.QUARANTINED)
    revision = models.PositiveBigIntegerField(default=0)
    fake_work_count = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class SyntheticClosureRequest(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    workspace = models.ForeignKey("workspaces.Workspace", on_delete=models.PROTECT)
    connection_id = models.UUIDField(editable=False)
    generation = models.UUIDField(editable=False)
    revision = models.PositiveBigIntegerField(default=0)
    initial_snapshot = models.JSONField()
    state = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("workspace", "connection_id"),
                name="unique_synthetic_closure_connection",
            ),
        ]


class SyntheticClosureOperation(models.Model):
    """Permanent issuance receipt within this synthetic experiment, not a job."""

    id = models.UUIDField(primary_key=True, editable=False)
    request = models.ForeignKey(SyntheticClosureRequest, on_delete=models.PROTECT)
    source_step = models.CharField(max_length=24)
    outcome = models.CharField(max_length=24)
    issued_revision = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(issued_revision__gt=0),
                name="synthetic_operation_positive_revision",
            ),
            models.UniqueConstraint(
                fields=("request", "issued_revision"),
                name="unique_synthetic_issuance_revision",
            ),
        ]


class ConnectorIdentity(models.Model):
    """Metadata foundation only. No activation, account ID, grant or runtime use."""

    class State(models.TextChoices):
        QUARANTINED = "quarantined"
        BLOCKED = "blocked"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    workspace = models.ForeignKey("workspaces.Workspace", on_delete=models.PROTECT)
    provider = models.CharField(
        max_length=24, default="google_ads_test", editable=False
    )
    generation = models.UUIDField(default=uuid4, editable=False)
    ordinal = models.PositiveBigIntegerField(default=1)
    revision = models.PositiveBigIntegerField(default=0)
    state = models.CharField(max_length=16, choices=State, default=State.QUARANTINED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("workspace", "provider"),
                name="unique_connector_workspace_provider",
            ),
            models.CheckConstraint(
                condition=models.Q(provider="google_ads_test"),
                name="connector_test_provider_only",
            ),
            models.CheckConstraint(
                condition=models.Q(state__in=("quarantined", "blocked")),
                name="connector_closed_states_only",
            ),
            models.CheckConstraint(
                condition=models.Q(ordinal__gt=0), name="connector_positive_ordinal"
            ),
        ]


class ConnectorGeneration(models.Model):
    """Permanent generation/request receipt; contains no credential material."""

    id = models.UUIDField(primary_key=True, editable=False)
    connection = models.ForeignKey(ConnectorIdentity, on_delete=models.PROTECT)
    request_id = models.UUIDField(unique=True, editable=False)
    ordinal = models.PositiveBigIntegerField()
    from_generation = models.UUIDField(null=True, editable=False)
    from_revision = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("connection", "ordinal"),
                name="unique_connector_generation_ordinal",
            ),
            models.CheckConstraint(
                condition=models.Q(ordinal__gt=0), name="connector_generation_positive"
            ),
        ]


class SyntheticAuthorizationAttempt(models.Model):
    """Fixed-example attempt receipt, never OAuth state, code, PKCE or a grant."""

    class State(models.TextChoices):
        PENDING = "pending"
        RUNNING = "running"
        ACCEPTED = "accepted"
        REJECTED = "rejected"
        EXPIRED = "expired"

    id = models.UUIDField(primary_key=True, editable=False)
    connection = models.ForeignKey(ConnectorIdentity, on_delete=models.PROTECT)
    generation = models.UUIDField(editable=False)
    expected_revision = models.PositiveBigIntegerField()
    mode = models.CharField(max_length=16, default="synthetic", editable=False)
    scenario = models.CharField(
        max_length=16,
        choices=(("allow_example", "Allow example"), ("deny_example", "Deny example")),
    )
    state = models.CharField(max_length=16, choices=State, default=State.PENDING)
    reason = models.CharField(max_length=24, default="", blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    expires_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, editable=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(mode="synthetic"), name="auth_attempt_synthetic_only"
            ),
            models.CheckConstraint(
                condition=models.Q(scenario__in=("allow_example", "deny_example")),
                name="auth_attempt_fixed_scenario",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    state__in=("pending", "running", "accepted", "rejected", "expired")
                ),
                name="auth_attempt_known_state",
            ),
            models.CheckConstraint(
                condition=models.Q(expires_at__gt=models.F("created_at")),
                name="auth_attempt_positive_lifetime",
            ),
            models.UniqueConstraint(
                fields=("connection",),
                condition=models.Q(state__in=("pending", "running")),
                name="unique_active_synthetic_auth",
            ),
        ]


class ScopedOAuthCandidateAttempt(models.Model):
    """TEST adapter receipt only; no token/code/query/state/verifier or file path."""

    class State(models.TextChoices):
        RESERVED = "reserved"
        EXCHANGING = "exchanging"
        CANDIDATE = "candidate"
        REJECTED = "rejected"
        UNCERTAIN = "uncertain"

    id = models.UUIDField(primary_key=True, editable=False)
    connection = models.ForeignKey(ConnectorIdentity, on_delete=models.PROTECT)
    generation = models.UUIDField(editable=False)
    expected_revision = models.PositiveBigIntegerField()
    session_key_hash = models.CharField(max_length=64, editable=False)
    client_id_hash = models.CharField(max_length=64, editable=False)
    state = models.CharField(max_length=16, choices=State, default=State.RESERVED)
    reason = models.CharField(max_length=24, blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    expires_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("connection", "generation"),
                name="unique_scoped_oauth_generation",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    state__in=(
                        "reserved",
                        "exchanging",
                        "candidate",
                        "rejected",
                        "uncertain",
                    )
                ),
                name="scoped_oauth_known_state",
            ),
            models.CheckConstraint(
                condition=models.Q(expires_at__gt=models.F("created_at")),
                name="scoped_oauth_positive_lifetime",
            ),
        ]
