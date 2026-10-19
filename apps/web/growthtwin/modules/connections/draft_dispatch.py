"""Local-only, durable PAUSED TEST dispatch of an approved creative snapshot."""

import hashlib
import json
import re
import threading
from datetime import date
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import connection, transaction
from django.views.decorators.debug import sensitive_variables

from growthtwin.modules.campaigns.google_draft_payload import build_draft_package
from growthtwin.modules.campaigns.models import (
    GoogleDraftApproval,
    GoogleDraftDispatch,
    WorkspaceCampaignDraft,
)

from . import backend, test_campaign, verification

_LOCK = threading.Lock()
_request = test_campaign._request


def profile(package):
    """Explicit test-only changes; original package/URL remain untouched."""
    google = json.loads(package.payload_json)["google"]
    start, end = date.fromisoformat(google["start"]), date.fromisoformat(google["end"])
    days = (end - start).days + 1
    if (
        google["target_city"] != "Ankara"
        or start < date.today()
        or days < 1
        or google["media_budget_minor"] < 1
    ):
        raise ValidationError("Bu test için ileri tarihli Ankara planı gerekli.")
    return {
        "version": "workspace-paused-test-v2-total",
        "original_url": google["final_url"],
        "test_url": "https://example.com/",
        "destination_note": "Public documentation placeholder; not a verified advertiser landing page",
        "currency": "TRY",
        "schedule_timezone": "Europe/Istanbul (account must match)",
        "total_micros": str(google["media_budget_minor"] * 10000),
        "period": "CUSTOM_PERIOD",
        "budget_semantics": "Exact campaign total TRY minor units * 10000; non-shared CUSTOM_PERIOD; TEST account only",
        "start": start.isoformat(),
        "end": end.isoformat(),
        "geo_lookup": {"name": "Ankara", "country": "TR", "type": "City"},
        "keyword": "growthtwin synthetic test",
        "match_type": "EXACT",
        "status": "PAUSED",
    }


def review_key(package):
    return hashlib.sha256(
        (package.fingerprint + json.dumps(profile(package), sort_keys=True)).encode()
    ).hexdigest()


def _name(row):
    return "GrowthTwin workspace test " + str(row.operation_id)


def budget_spec(plan):
    """Read immutable stored version; never reinterpret a daily ledger as total."""
    if plan["version"] == "workspace-paused-test-v1":
        return "DAILY", "amountMicros", plan["daily_micros"], "totalAmountMicros"
    if (
        plan["version"] == "workspace-paused-test-v2-total"
        and plan["period"] == "CUSTOM_PERIOD"
    ):
        return (
            "CUSTOM_PERIOD",
            "totalAmountMicros",
            plan["total_micros"],
            "amountMicros",
        )
    raise ValidationError("Desteklenmeyen test bütçe sürümü.")


def _operations(customer, row):
    stored = json.loads(row.payload_json)
    google, plan = stored["package"]["google"], stored["test_profile"]
    operations = test_campaign._create_operations(customer, row)
    old_name = test_campaign._name(row)
    for item in operations:
        create = next(iter(item.values()))["create"]
        if "name" in create:
            create["name"] = create["name"].replace(old_name, _name(row))
    period, field, amount, other = budget_spec(plan)
    budget = operations[0]["campaignBudgetOperation"]["create"]
    budget.pop(other, None)
    budget.update({"period": period, field: amount})
    campaign = operations[1]["campaignOperation"]["create"]
    campaign.update(
        startDateTime=plan["start"] + " 00:00:00", endDateTime=plan["end"] + " 23:59:59"
    )
    campaign["geoTargetTypeSetting"] = {"positiveGeoTargetType": "PRESENCE"}
    ad = operations[4]["adGroupAdOperation"]["create"]["ad"]
    ad["finalUrls"] = [plan["test_url"]]
    ad["responsiveSearchAd"] = {
        "headlines": [{"text": text} for text in google["headlines"]],
        "descriptions": [{"text": text} for text in google["descriptions"]],
    }
    operations.append(
        {
            "campaignCriterionOperation": {
                "create": {
                    "campaign": campaign["resourceName"],
                    "location": {"geoTargetConstant": stored["geo_resource"]},
                }
            }
        }
    )
    return operations


def _resolve(binding):
    result = _request(
        binding,
        "googleAds:search",
        {
            "query": (
                "SELECT geo_target_constant.resource_name, geo_target_constant.name, "
                "geo_target_constant.country_code, geo_target_constant.target_type, geo_target_constant.status "
                "FROM geo_target_constant WHERE geo_target_constant.name = 'Ankara' "
                "AND geo_target_constant.country_code = 'TR' AND geo_target_constant.target_type = 'City' LIMIT 2"
            )
        },
    )
    rows = result.get("results", [])
    if result.get("nextPageToken") or len(rows) != 1:
        raise ValueError
    geo = rows[0]["geoTargetConstant"]
    if (
        geo.get("name") != "Ankara"
        or geo.get("countryCode") != "TR"
        or geo.get("targetType") != "City"
        or geo.get("status") != "ENABLED"
        or not re.fullmatch(r"geoTargetConstants/[0-9]+", geo.get("resourceName", ""))
    ):
        raise ValueError
    account = _request(
        binding,
        "googleAds:search",
        {
            "query": "SELECT customer.currency_code, customer.time_zone FROM customer LIMIT 1"
        },
    )
    if (
        account.get("nextPageToken")
        or len(account.get("results", [])) != 1
        or account["results"][0]["customer"].get("currencyCode") != "TRY"
    ):
        raise ValueError
    if account["results"][0]["customer"].get("timeZone") not in {
        "Europe/Istanbul",
        "Asia/Istanbul",
    }:
        raise ValueError
    return geo["resourceName"]


def _current(binding, draft_id):
    draft = WorkspaceCampaignDraft.objects.get(
        pk=draft_id, workspace_id=binding[1], workspace__owner_id=binding[0]
    )
    package = build_draft_package(draft)
    key = verification.configuration_key(binding)
    approval = GoogleDraftApproval.objects.get(
        draft=draft,
        fingerprint=package.fingerprint,
        target_key=key,
        payload_json=package.payload_json,
    )
    return draft, package, key, approval


@sensitive_variables()
def _read(binding, row, customer, *, for_stop=False):
    expected = json.loads(row.payload_json)
    result = _request(
        binding,
        "googleAds:search",
        {
            "query": (
                "SELECT campaign.resource_name, campaign.name, campaign.status, campaign.campaign_budget, "
                "campaign.advertising_channel_type, campaign.start_date_time, campaign.end_date_time, campaign.geo_target_type_setting.positive_geo_target_type, "
                "campaign_budget.resource_name, campaign_budget.name, campaign_budget.amount_micros, campaign_budget.total_amount_micros, campaign_budget.period, "
                "campaign_budget.explicitly_shared FROM campaign WHERE campaign.name = '"
                + _name(row)
                + "' LIMIT 2"
            )
        },
    )
    rows = result.get("results", [])
    if result.get("nextPageToken") or len(rows) != 1:
        raise ValueError
    campaign, budget = rows[0]["campaign"], rows[0]["campaignBudget"]
    resource = campaign.get("resourceName")
    if (
        not test_campaign._campaign_resource(resource, customer)
        or (row.resource_name and row.resource_name != resource)
        or campaign.get("name") != _name(row)
        or campaign.get("advertisingChannelType") != "SEARCH"
        or campaign.get("campaignBudget") != budget.get("resourceName")
        or not re.fullmatch(
            rf"customers/{customer}/campaignBudgets/[0-9]+",
            budget.get("resourceName", ""),
        )
        or budget.get("name") not in {_name(row), _name(row) + " budget"}
        or verification.configuration_key(binding) != row.configuration_key
    ):
        raise ValueError
    if not for_stop:
        period, field, amount, other = budget_spec(expected["test_profile"])
        if (
            budget.get("period") != period
            or str(budget.get(field)) != amount
            or str(budget.get(other, "0")) != "0"
            or budget.get("explicitlyShared", False) is not False
            or campaign.get("startDateTime")
            != expected["test_profile"]["start"] + " 00:00:00"
            or campaign.get("endDateTime")
            != expected["test_profile"]["end"] + " 23:59:59"
            or campaign.get("geoTargetTypeSetting", {}).get("positiveGeoTargetType")
            != "PRESENCE"
        ):
            raise ValueError
        ads = _request(
            binding,
            "googleAds:search",
            {
                "query": (
                    "SELECT ad_group.status, ad_group_ad.status, ad_group_ad.ad.final_urls, "
                    "ad_group_ad.ad.responsive_search_ad.headlines, ad_group_ad.ad.responsive_search_ad.descriptions "
                    "FROM ad_group_ad WHERE campaign.resource_name = '"
                    + resource
                    + "' LIMIT 2"
                )
            },
        )
        if ads.get("nextPageToken") or len(ads.get("results", [])) != 1:
            raise ValueError
        item = ads["results"][0]
        ad = item["adGroupAd"]["ad"]
        if (
            item["adGroup"].get("status") != "PAUSED"
            or item["adGroupAd"].get("status") != "PAUSED"
            or ad.get("finalUrls") != [expected["test_profile"]["test_url"]]
            or any(
                sorted(x["text"] for x in ad["responsiveSearchAd"][field])
                != sorted(expected["package"]["google"][field])
                for field in ("headlines", "descriptions")
            )
        ):
            raise ValueError
        locations = _request(
            binding,
            "googleAds:search",
            {
                "query": (
                    "SELECT campaign_criterion.location.geo_target_constant, campaign_criterion.negative "
                    "FROM campaign_criterion WHERE campaign.resource_name = '"
                    + resource
                    + "' AND campaign_criterion.type = 'LOCATION' LIMIT 2"
                )
            },
        )
        location_rows = locations.get("results", [])
        if (
            locations.get("nextPageToken")
            or len(location_rows) != 1
            or location_rows[0]["campaignCriterion"]["location"].get(
                "geoTargetConstant"
            )
            != expected["geo_resource"]
            or location_rows[0]["campaignCriterion"].get("negative", False)
        ):
            raise ValueError
        keywords = _request(
            binding,
            "googleAds:search",
            {
                "query": (
                    "SELECT ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, ad_group_criterion.status "
                    "FROM ad_group_criterion WHERE campaign.resource_name = '"
                    + resource
                    + "' AND ad_group_criterion.type = 'KEYWORD' LIMIT 2"
                )
            },
        )
        keyword_rows = keywords.get("results", [])
        if (
            keywords.get("nextPageToken")
            or len(keyword_rows) != 1
            or keyword_rows[0]["adGroupCriterion"].get("status") != "PAUSED"
            or keyword_rows[0]["adGroupCriterion"].get("keyword")
            != {"text": expected["test_profile"]["keyword"], "matchType": "EXACT"}
        ):
            raise ValueError
    row.resource_name = resource
    row.observed_status = campaign.get("status", "")
    row.state = (
        ("stopped" if row.state == "stopped" else "paused")
        if row.observed_status == "PAUSED"
        else "uncertain"
    )
    row.save(update_fields=["resource_name", "observed_status", "state", "updated_at"])
    return row


@sensitive_variables()
def perform(binding, draft_id, action, consent_key=""):
    with _LOCK:
        backend._enabled()
        if (
            not getattr(settings, "GOOGLE_ADS_LOCAL_TEST_CAMPAIGN_ENABLED", False)
            or action not in {"create", "read", "stop"}
            or connection.in_atomic_block
        ):
            raise backend.ConnectionUnavailable("Test dispatch unavailable.")
        key = verification.configuration_key(binding)
        draft = WorkspaceCampaignDraft.objects.get(
            pk=draft_id, workspace_id=binding[1], workspace__owner_id=binding[0]
        )
        row = GoogleDraftDispatch.objects.filter(draft=draft).first()
        if row and row.configuration_key != key:
            raise backend.ConnectionUnavailable("Target changed.")
        if row and action == "create":
            stored = json.loads(row.payload_json)["test_profile"]
            if stored["version"] != "workspace-paused-test-v2-total":
                raise ValidationError(
                    "Bu taslağın günlük bütçeli test kaydı korunuyor; toplam bütçe için yeni sentetik taslak oluşturun."
                )
        if verification.verify(binding) != key:
            raise backend.ConnectionUnavailable("Test target unavailable.")
        customer, _ = verification._targets()
        reserved = False
        if row is None:
            if action != "create":
                raise backend.ConnectionUnavailable("No dispatch intent.")
            _, package, _, approval = _current(binding, draft_id)
            if consent_key != review_key(package):
                raise ValidationError("Test plan changed.")
            candidate = GoogleDraftDispatch(
                draft=draft,
                approval=approval,
                configuration_key=key,
                operation_id=uuid4(),
                payload_json=json.dumps(
                    {
                        "package": json.loads(package.payload_json),
                        "test_profile": profile(package),
                        "geo_resource": _resolve(binding),
                    },
                    sort_keys=True,
                    ensure_ascii=False,
                ),
            )
            operations = _operations(customer, candidate)
            _request(
                binding,
                "googleAds:mutate",
                {
                    "mutateOperations": operations,
                    "validateOnly": True,
                    "partialFailure": False,
                },
            )
            # Recheck after all preparation, then commit intent before any write.
            with transaction.atomic():
                WorkspaceCampaignDraft.objects.select_for_update().get(pk=draft.pk)
                _, latest, latest_key, _ = _current(binding, draft_id)
                if latest_key != key or latest != package:
                    raise ValidationError("Draft changed.")
                row, reserved = GoogleDraftDispatch.objects.get_or_create(
                    draft=draft,
                    defaults={
                        "approval": approval,
                        "configuration_key": key,
                        "operation_id": candidate.operation_id,
                        "payload_json": candidate.payload_json,
                    },
                )
        try:
            if reserved:
                if verification.verify(binding) != key:
                    raise ValueError
                _, current, current_key, _ = _current(binding, draft_id)
                if current_key != key or review_key(current) != consent_key:
                    raise ValueError
                _request(
                    binding,
                    "googleAds:mutate",
                    {
                        "mutateOperations": _operations(customer, row),
                        "partialFailure": False,
                    },
                )
            row = _read(binding, row, customer, for_stop=action == "stop")
            if action == "stop":
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
                row = _read(binding, row, customer)
                if row.state == "paused":
                    row.state = "stopped"
                    row.save(update_fields=["state", "updated_at"])
            return row
        except Exception:
            row.state, row.observed_status = "uncertain", ""
            row.save(update_fields=["state", "observed_status", "updated_at"])
            return row
