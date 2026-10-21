"""Isolated synthetic closure metadata, never credentials or campaign content."""

from django.db import models


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
