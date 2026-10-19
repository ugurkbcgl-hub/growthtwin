"""One durable, paused synthetic Google campaign per local workspace.

An uncertain create is never retried. Reads reconcile its deterministic name;
zero matches remain uncertain because remote visibility may be delayed.
"""

import json
import re
import threading
from urllib.error import HTTPError
from urllib.request import Request, build_opener
from uuid import uuid4

from django.conf import settings
from django.db import connection, transaction
from django.views.decorators.debug import sensitive_variables

from growthtwin.modules.campaigns.models import GoogleTestCampaign
from growthtwin.modules.workspaces.models import Workspace

from . import backend, verification
from .google_oauth import ADS_SCOPE

BUDGET_MICROS = "1000000"
_PROCESS_LOCK = threading.Lock()


class TestCampaignRejected(backend.ConnectionUnavailable):
    """Only allowlisted API enums may escape the private response body."""

    def __init__(self, category="UNAVAILABLE"):
        super().__init__("Google test campaign validation failed.")
        self.category = category


@sensitive_variables()
def _rejection(error):
    allowed = {
        "REQUIRED",
        "INVALID_VALUE",
        "RESOURCE_NOT_FOUND",
        "OPERATION_NOT_PERMITTED_FOR_CONTEXT",
        "USER_PERMISSION_DENIED",
        "AUTHORIZATION_ERROR",
        "CUSTOMER_NOT_ENABLED",
        "NOT_ADS_USER",
        "DEVELOPER_TOKEN_NOT_APPROVED",
        "REQUESTED_METRICS_FOR_MANAGER",
        "BUDGET_AMOUNT_TOO_SMALL",
        "CANNOT_USE_BIDDING_STRATEGY_TYPE",
        "INVALID_ARGUMENT",
        "PERMISSION_DENIED",
        "UNAUTHENTICATED",
    }
    try:
        payload = json.loads(error.read(65536))
        for detail in payload.get("error", {}).get("details", []):
            for item in detail.get("errors", []):
                for value in item.get("errorCode", {}).values():
                    if isinstance(value, str) and value in allowed:
                        return TestCampaignRejected(value)
    except Exception:
        pass
    finally:
        error.close()
    return TestCampaignRejected()


def _name(row):
    return "GrowthTwin synthetic test " + str(row.operation_id)


@sensitive_variables()
def _access_token(binding):
    saved = backend._read(backend._token_path(binding))
    client = backend._client()
    if saved.get("scope") != ADS_SCOPE:
        raise ValueError
    token = json.loads(
        backend._post(
            "https://oauth2.googleapis.com/token",
            {
                "client_id": client["client_id"],
                "client_secret": client["client_secret"],
                "refresh_token": saved["refresh_token"],
                "grant_type": "refresh_token",
            },
        )
    )
    if (
        not isinstance(token.get("access_token"), str)
        or not token["access_token"]
        or token.get("token_type", "").lower() != "bearer"
    ):
        raise ValueError
    return token["access_token"]


@sensitive_variables()
def _request(binding, operation, payload):
    customer, manager = verification._targets()
    if operation not in {"googleAds:search", "googleAds:mutate"}:
        raise ValueError
    request = Request(
        f"https://googleads.googleapis.com/v25/customers/{customer}/{operation}",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": "Bearer " + _access_token(binding),
            "login-customer-id": manager,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with build_opener(backend._NoRedirect()).open(request, timeout=25) as response:
            body = response.read(65537)
            if response.status != 200 or len(body) > 65536:
                raise ValueError
            result = json.loads(body)
            if not isinstance(result, dict) or result.get("partialFailureError"):
                raise ValueError
            return result
    except HTTPError as error:
        raise _rejection(error) from None


def _create_operations(customer, row):
    base = f"customers/{customer}"
    budget = base + "/campaignBudgets/-1"
    campaign = base + "/campaigns/-2"
    group = base + "/adGroups/-3"
    name = _name(row)
    return [
        {
            "campaignBudgetOperation": {
                "create": {
                    "resourceName": budget,
                    "name": name + " budget",
                    "amountMicros": BUDGET_MICROS,
                    "deliveryMethod": "STANDARD",
                    "explicitlyShared": False,
                }
            }
        },
        {
            "campaignOperation": {
                "create": {
                    "resourceName": campaign,
                    "name": name,
                    "status": "PAUSED",
                    "advertisingChannelType": "SEARCH",
                    "campaignBudget": budget,
                    "manualCpc": {},
                    "containsEuPoliticalAdvertising": "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING",
                    "networkSettings": {
                        "targetGoogleSearch": True,
                        "targetSearchNetwork": False,
                        "targetContentNetwork": False,
                        "targetPartnerSearchNetwork": False,
                    },
                }
            }
        },
        {
            "adGroupOperation": {
                "create": {
                    "resourceName": group,
                    "campaign": campaign,
                    "name": name + " group",
                    "status": "PAUSED",
                    "type": "SEARCH_STANDARD",
                    "cpcBidMicros": "100000",
                }
            }
        },
        {
            "adGroupCriterionOperation": {
                "create": {
                    "adGroup": group,
                    "status": "PAUSED",
                    "keyword": {
                        "text": "growthtwin synthetic test",
                        "matchType": "EXACT",
                    },
                }
            }
        },
        {
            "adGroupAdOperation": {
                "create": {
                    "adGroup": group,
                    "status": "PAUSED",
                    "ad": {
                        "finalUrls": ["https://example.com/"],
                        "responsiveSearchAd": {
                            "headlines": [
                                {"text": text}
                                for text in (
                                    "GrowthTwin Test",
                                    "Synthetic Campaign",
                                    "Test Account Only",
                                )
                            ],
                            "descriptions": [
                                {"text": text}
                                for text in (
                                    "Synthetic integration example. No real service is offered.",
                                    "For a paused Google test account integration only.",
                                )
                            ],
                        },
                    },
                }
            }
        },
    ]


def _campaign_resource(value, customer):
    return isinstance(value, str) and bool(
        re.fullmatch(rf"customers/{customer}/campaigns/[0-9]+", value)
    )


@sensitive_variables()
def _reconcile(binding, row, customer, *, for_stop=False):
    payload = _request(
        binding,
        "googleAds:search",
        {
            "query": (
                "SELECT campaign.resource_name, campaign.name, campaign.status, campaign.campaign_budget, "
                "campaign.advertising_channel_type, campaign_budget.name, "
                "campaign_budget.resource_name, campaign_budget.amount_micros, campaign_budget.explicitly_shared "
                "FROM campaign WHERE campaign.name = '" + _name(row) + "' LIMIT 2"
            )
        },
    )
    results = payload.get("results", [])
    if payload.get("nextPageToken") or len(results) != 1:
        raise ValueError
    campaign = results[0]["campaign"]
    budget = results[0]["campaignBudget"]
    resource = campaign.get("resourceName")
    if (
        not _campaign_resource(resource, customer)
        or (row.resource_name and resource != row.resource_name)
        or campaign.get("name") != _name(row)
        or campaign.get("advertisingChannelType") != "SEARCH"
        or budget.get("name") not in {_name(row), _name(row) + " budget"}
        or not isinstance(budget.get("resourceName"), str)
        or not re.fullmatch(
            rf"customers/{customer}/campaignBudgets/[0-9]+", budget["resourceName"]
        )
        or campaign.get("campaignBudget") != budget["resourceName"]
        or str(budget.get("amountMicros")) != BUDGET_MICROS
        or budget.get("explicitlyShared", False) is not False
        or (not for_stop and campaign.get("status") not in {"PAUSED", "REMOVED"})
        or verification.configuration_key(binding) != row.configuration_key
    ):
        raise ValueError
    row.resource_name = resource
    status = campaign.get("status")
    row.observed_status = status if status in {"PAUSED", "REMOVED"} else "UNEXPECTED"
    row.state = {
        "PAUSED": "stopped" if row.state == "stopped" else "paused",
        "REMOVED": "removed",
    }.get(status, "uncertain")
    row.save(update_fields=["resource_name", "observed_status", "state", "updated_at"])
    return row


@sensitive_variables()
def _perform(binding, action):
    """Execute only an explicitly requested local owner action; never re-create."""
    backend._enabled()
    if (
        not getattr(settings, "GOOGLE_ADS_LOCAL_TEST_CAMPAIGN_ENABLED", False)
        or action not in {"create", "read", "stop"}
        or connection.in_atomic_block
    ):
        raise backend.ConnectionUnavailable("Test campaign action is unavailable.")
    # Validates configured binding and existing encrypted grant before DB access.
    key = verification.configuration_key(binding)
    workspace = Workspace.objects.get(pk=binding[1], owner_id=binding[0])
    customer, _ = verification._targets()
    if verification.verify(binding) != key:
        raise backend.ConnectionUnavailable("Test campaign verification failed.")
    created = False
    row = GoogleTestCampaign.objects.filter(workspace=workspace).first()
    if row is None:
        if action != "create":
            raise backend.ConnectionUnavailable("No test campaign intent exists.")
        candidate = GoogleTestCampaign(
            workspace=workspace, configuration_key=key, operation_id=uuid4()
        )
        try:
            _request(
                binding,
                "googleAds:mutate",
                {
                    "mutateOperations": _create_operations(customer, candidate),
                    "partialFailure": False,
                    "validateOnly": True,
                },
            )
        except TestCampaignRejected:
            raise
        except Exception:
            raise backend.ConnectionUnavailable(
                "Google test campaign validation failed."
            ) from None
        if verification.configuration_key(binding) != key:
            raise backend.ConnectionUnavailable("Test campaign configuration changed.")
        with transaction.atomic():
            row, created = GoogleTestCampaign.objects.get_or_create(
                workspace=workspace,
                defaults={
                    "configuration_key": key,
                    "operation_id": candidate.operation_id,
                },
            )
    # The reservation is now committed. Never delete or reset it on errors.
    if row.configuration_key != key:
        raise backend.ConnectionUnavailable("Test campaign configuration changed.")
    try:
        if action == "create" and created:
            if verification.verify(binding) != key:
                raise ValueError
            _request(
                binding,
                "googleAds:mutate",
                {
                    "mutateOperations": _create_operations(customer, row),
                    "partialFailure": False,
                },
            )
        # Existing create requests only read; ambiguous requests are never resent.
        row = _reconcile(binding, row, customer, for_stop=action == "stop")
        if action == "stop" and row.state != "removed":
            if verification.verify(binding) != key:
                raise ValueError
            _request(
                binding,
                "googleAds:mutate",
                {
                    "mutateOperations": [
                        {
                            "campaignOperation": {
                                "update": {
                                    "resourceName": row.resource_name,
                                    "status": "PAUSED",
                                },
                                "updateMask": "status",
                            }
                        }
                    ],
                    "partialFailure": False,
                },
            )
            row = _reconcile(binding, row, customer)
            if row.state == "paused":
                row.state = "stopped"
                row.save(update_fields=["state", "updated_at"])
        return row
    except Exception:
        row.state = "uncertain"
        row.observed_status = ""
        row.save(update_fields=["state", "observed_status", "updated_at"])
        return row


@sensitive_variables()
def perform(binding, action):
    # Serialize local lifecycle actions; DB uniqueness also protects reservation.
    with _PROCESS_LOCK:
        return _perform(binding, action)
