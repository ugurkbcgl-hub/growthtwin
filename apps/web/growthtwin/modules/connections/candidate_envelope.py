"""Strict candidate-only codec. Validation never returns credential material."""

from django.views.decorators.debug import sensitive_variables

from .google_oauth import ADS_SCOPE


def _binding(*, owner_id, workspace_id, receipt):
    return {
        "schema": "google-test-candidate-v1",
        "owner_id": str(owner_id),
        "workspace_id": str(workspace_id),
        "connection_id": str(receipt.connection_id),
        "generation": str(receipt.generation),
        "attempt_id": str(receipt.pk),
        "client_id_hash": receipt.client_id_hash,
        "scope": ADS_SCOPE,
    }


@sensitive_variables()
def validate_envelope(value, *, owner_id, workspace_id, receipt):
    expected = _binding(owner_id=owner_id, workspace_id=workspace_id, receipt=receipt)
    if type(value) is not dict or set(value) != set(expected) | {"refresh_token"}:
        return False
    if any(
        type(value[key]) is not str or value[key] != item
        for key, item in expected.items()
    ):
        return False
    token = value["refresh_token"]
    return (
        type(token) is str
        and 1 <= len(token) <= 8192
        and all(33 <= ord(character) <= 126 for character in token)
    )


@sensitive_variables()
def build_envelope(*, owner_id, workspace_id, receipt, refresh_token):
    value = _binding(owner_id=owner_id, workspace_id=workspace_id, receipt=receipt)
    value["refresh_token"] = refresh_token
    if not validate_envelope(
        value, owner_id=owner_id, workspace_id=workspace_id, receipt=receipt
    ):
        raise ValueError("Invalid candidate envelope.")
    return value
