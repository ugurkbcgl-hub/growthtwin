"""Owner-scoped synthetic publishing lifecycle with optimistic form revisions."""

import hashlib
import json
import uuid

from django.core.exceptions import ValidationError
from django.db import transaction

from growthtwin.modules.campaigns.models import (
    CampaignRehearsal,
    WorkspaceCampaignDraft,
)
from growthtwin.modules.campaigns.planning import build_google_search_campaign_plan
from growthtwin.modules.campaigns.services import creative_source_hash_for_draft
from growthtwin.modules.publishing.fake import start_rehearsal, stop_rehearsal


def _snapshot(draft):
    current = (draft.creative_versions or [None])[-1]
    selected = next(
        (
            v
            for v in (current or {}).get("variants", [])
            if v.get("key") == draft.preferred_creative_key
        ),
        None,
    )
    source_hash = creative_source_hash_for_draft(draft)
    ready = bool(
        current
        and selected
        and current.get("source_hash") == source_hash
        and current.get("version") == draft.preferred_creative_version
        and build_google_search_campaign_plan(draft).ready_for_review
    )
    payload = {
        "source": source_hash,
        "selected": selected,
        "version": draft.preferred_creative_version,
        "key": draft.preferred_creative_key,
        "channel": draft.channel,
        "budget": draft.media_budget_minor,
        "currency": draft.currency,
        "start": str(draft.flight_start),
        "end": str(draft.flight_end),
        "destination": draft.destination_url,
    }
    fingerprint = hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return ready, fingerprint


def rehearsal_context(draft):
    """Read-only presentation snapshot; never materializes a missing state row."""
    rehearsal = CampaignRehearsal.objects.filter(draft=draft).first()
    ready, fingerprint = _snapshot(draft)
    state = rehearsal.state if rehearsal else CampaignRehearsal.State.IDLE
    stale = bool(
        rehearsal
        and state in ("running", "failed")
        and rehearsal.fingerprint != fingerprint
    )
    return {
        "state": state,
        "state_label": CampaignRehearsal.State(state).label,
        "revision": rehearsal.revision if rehearsal else 0,
        "fingerprint": fingerprint,
        "can_start": ready and state in ("idle", "stopped"),
        "can_retry": ready and state == "failed" and not stale,
        "can_stop": state in ("running", "failed"),
        "stale": stale,
        "events": list(rehearsal.events.all()[:20]) if rehearsal else [],
    }


@transaction.atomic
def perform_campaign_rehearsal(
    *, owner, draft_id, action, expected_revision, expected_fingerprint
):
    """Lock the owner campaign, reject stale commands, and persist one transition."""
    draft = (
        WorkspaceCampaignDraft.objects.owned_by(owner)
        .select_for_update()
        .get(pk=draft_id)
    )
    rehearsal = CampaignRehearsal.objects.filter(draft=draft).first()
    revision = rehearsal.revision if rehearsal else 0
    if type(expected_revision) is not int or expected_revision != revision:
        raise ValidationError("Prova değişti. Sayfayı yenileyip tekrar dene.")
    if action not in ("start", "start_failure", "retry", "stop"):
        raise ValidationError("Bilinmeyen prova işlemi.")
    state = rehearsal.state if rehearsal else "idle"
    ready, fingerprint = _snapshot(draft)
    if action == "stop":
        if state not in ("running", "failed"):
            raise ValidationError("Durdurulabilecek bir prova yok.")
        result = stop_rehearsal(rehearsal.operation_id)
    else:
        if not ready or expected_fingerprint != fingerprint:
            raise ValidationError(
                "Güncel metin seçimi ve eksiksiz kampanya planı gerekli."
            )
        if action == "retry":
            if state != "failed" or rehearsal.fingerprint != fingerprint:
                raise ValidationError("Bu prova yeniden denenemez.")
        else:
            if state not in ("idle", "stopped"):
                raise ValidationError("Yeni prova için mevcut provayı durdur.")
            if rehearsal is None:
                rehearsal = CampaignRehearsal(draft=draft)
            rehearsal.operation_id = uuid.uuid4()
            rehearsal.fingerprint = fingerprint
        result = start_rehearsal(rehearsal.operation_id, fail=action == "start_failure")
    rehearsal.state = result.state
    rehearsal.receipt = result.receipt
    rehearsal.revision = revision + 1
    rehearsal.save()
    rehearsal.events.create(
        revision=rehearsal.revision,
        action=action,
        state=rehearsal.state,
        operation_id=rehearsal.operation_id,
        receipt=rehearsal.receipt,
    )
    return rehearsal
