"""Validate a campaign-total-budget candidate in TEST; never create resources."""

import hashlib
import json
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import connection
from django.views.decorators.debug import sensitive_variables

from growthtwin.modules.campaigns.models import GoogleDraftDispatch

from . import backend, draft_dispatch, verification


def plan(package):
    """A separate review identity: no change to daily-budget dispatch v1."""
    source = json.loads(package.payload_json)["google"]
    inherited = draft_dispatch.profile(package)
    return {
        "version": "google-search-total-budget-validation-v1",
        "total_micros": str(source["media_budget_minor"] * 10000),
        "currency": source["currency"],
        "period": "CUSTOM_PERIOD",
        "explicitly_shared": False,
        "start": inherited["start"],
        "end": inherited["end"],
        "timezone": inherited["schedule_timezone"],
        "test_url": inherited["test_url"],
        "test_profile": inherited,
        "validate_only": True,
    }


def review_key(package):
    return hashlib.sha256(
        (package.fingerprint + json.dumps(plan(package), sort_keys=True)).encode()
    ).hexdigest()


def operations(customer, candidate):
    """Only replace budget fields in a fresh in-memory TEST candidate."""
    stored = json.loads(candidate.payload_json)
    result = draft_dispatch._operations(customer, candidate)
    budget = result[0]["campaignBudgetOperation"]["create"]
    budget.pop("amountMicros")
    budget["period"] = "CUSTOM_PERIOD"
    budget["totalAmountMicros"] = stored["total_budget"]["total_micros"]
    budget["explicitlyShared"] = False
    return result


@sensitive_variables()
def _validate(binding, draft_id, consent_key):
    backend._enabled()
    if (
        not getattr(settings, "GOOGLE_ADS_LOCAL_TEST_CAMPAIGN_ENABLED", False)
        or connection.in_atomic_block
    ):
        raise backend.ConnectionUnavailable("TEST budget validation unavailable.")
    draft, package, key, approval = draft_dispatch._current(binding, draft_id)
    if review_key(package) != consent_key:
        raise ValidationError("Budget review changed.")
    if verification.verify(binding) != key:
        raise backend.ConnectionUnavailable("TEST target not verified.")
    geo_resource = draft_dispatch._resolve(binding)
    candidate = GoogleDraftDispatch(
        draft=draft,
        approval=approval,
        operation_id=uuid4(),
        configuration_key=key,
        payload_json=json.dumps(
            {
                "package": json.loads(package.payload_json),
                "test_profile": draft_dispatch.profile(package),
                "total_budget": plan(package),
                "geo_resource": geo_resource,
            },
            sort_keys=True,
            ensure_ascii=False,
        ),
    )
    # Reads above may take time: recheck source and grant before validation.
    _, current, current_key, _ = draft_dispatch._current(binding, draft_id)
    if current != package or current_key != key:
        raise ValidationError("Budget source changed.")
    customer, _ = verification._targets()
    draft_dispatch._request(
        binding,
        "googleAds:mutate",
        {
            "mutateOperations": operations(customer, candidate),
            "partialFailure": False,
            "validateOnly": True,
        },
    )
    _, current, current_key, _ = draft_dispatch._current(binding, draft_id)
    if current != package or current_key != key:
        raise ValidationError("Budget evidence became stale.")
    # No save, reservation, creation, fallback or live enable operation exists.
    return plan(package)


@sensitive_variables()
def validate(binding, draft_id, consent_key):
    try:
        return _validate(binding, draft_id, consent_key)
    except (OSError, KeyError, TypeError, ValueError, AttributeError, IndexError):
        # urllib network/timeouts and malformed provider bodies never escape.
        raise backend.ConnectionUnavailable(
            "TEST budget validation unavailable."
        ) from None
