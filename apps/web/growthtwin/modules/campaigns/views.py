"""Authenticated views for local synthetic campaign planning."""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import number_format
from django.views.decorators.http import require_POST

from growthtwin.modules.campaigns.forms import (
    CampaignDraftEditForm,
    CampaignDraftForm,
)
from growthtwin.modules.campaigns.models import WorkspaceCampaignDraft
from growthtwin.modules.campaigns.planning import build_google_search_campaign_plan
from growthtwin.modules.campaigns.services import (
    create_campaign_draft_for_owner,
    creative_source_hash_for_draft,
    generate_creative_version_for_owner,
    select_preferred_creative_for_owner,
    update_campaign_draft_for_owner,
)
from growthtwin.modules.workspaces.models import Workspace

SYNTHETIC_CAMPAIGN = {
    "name": "Sentetik Ankara ev bakım kampanyası",
    "brand_name": "Başkent Ev Bakım (Sentetik)",
    "brief": "Ankara'da ev bakım ve onarım hizmeti için teklif talepleri alın.",
    "target_city": "Ankara",
    "destination_url": "https://example.invalid/ev-bakim",
    "media_budget_minor": 500_000,
}


def _workspaces_for_user(user):
    workspaces = Workspace.objects.filter(owner=user)
    if not workspaces.exists():
        Workspace.objects.create(owner=user, name="Kişisel çalışma alanı")
        workspaces = Workspace.objects.filter(owner=user)
    return workspaces


def _draft_rows(drafts):
    return [
        {
            "draft": draft,
            "budget_display": _format_budget(draft.media_budget_minor),
        }
        for draft in drafts
    ]


def _format_budget(minor_units):
    amount = Decimal(minor_units) / 100
    return f"{number_format(amount, decimal_pos=2, force_grouping=True)} TRY"


def _format_daily_average(minor_units):
    if minor_units is None:
        return None
    amount = minor_units / 100
    return f"{number_format(amount, decimal_pos=2, force_grouping=True)} TRY"


@login_required
def campaign_list(request):
    """Show only the current user's workspace campaign drafts."""

    _workspaces_for_user(request.user)
    drafts = WorkspaceCampaignDraft.objects.owned_by(request.user).select_related(
        "workspace"
    )
    return render(
        request,
        "campaigns/list.html",
        {"draft_rows": _draft_rows(drafts), "synthetic_only": True},
    )


@login_required
def campaign_create(request):
    """Create an owner-scoped synthetic campaign draft and show its local plan."""

    workspaces = _workspaces_for_user(request.user)
    form = CampaignDraftForm(
        request.POST or None,
        workspaces=workspaces,
    )
    if request.method == "POST" and form.is_valid():
        values = form.cleaned_data
        today = timezone.localdate()
        draft = create_campaign_draft_for_owner(
            owner=request.user,
            workspace_id=values["workspace"].pk,
            name=SYNTHETIC_CAMPAIGN["name"],
            brand_name=SYNTHETIC_CAMPAIGN["brand_name"],
            brief=SYNTHETIC_CAMPAIGN["brief"],
            target_city=SYNTHETIC_CAMPAIGN["target_city"],
            destination_url=SYNTHETIC_CAMPAIGN["destination_url"],
            media_budget_minor=SYNTHETIC_CAMPAIGN["media_budget_minor"],
            currency="TRY",
            flight_start=today + timedelta(days=1),
            flight_end=today + timedelta(days=15),
        )
        generate_creative_version_for_owner(owner=request.user, draft_id=draft.pk)
        return redirect("campaigns:detail", draft_id=draft.pk)

    return render(
        request,
        "campaigns/create.html",
        {"form": form, "sample": SYNTHETIC_CAMPAIGN},
    )


@login_required
def campaign_detail(request, draft_id):
    """Render an owner's local plan; cross-tenant IDs resolve as not found."""

    draft = get_object_or_404(
        WorkspaceCampaignDraft.objects.owned_by(request.user).select_related(
            "workspace"
        ),
        pk=draft_id,
    )
    plan = build_google_search_campaign_plan(draft)
    versions = draft.creative_versions or []
    latest_creative_version = versions[-1] if versions else None
    creative_is_stale = bool(
        latest_creative_version
        and latest_creative_version.get("source_hash")
        != creative_source_hash_for_draft(draft)
    )
    return render(
        request,
        "campaigns/detail.html",
        {
            "draft": draft,
            "plan": plan,
            "budget_display": _format_budget(draft.media_budget_minor),
            "daily_average_display": _format_daily_average(
                plan.daily_media_average_minor
            ),
            "creative_version": (
                latest_creative_version if not creative_is_stale else None
            ),
            "creative_is_stale": creative_is_stale,
            "creative_version_count": len(versions),
            "preferred_creative_key": (
                draft.preferred_creative_key
                if (
                    not creative_is_stale
                    and latest_creative_version
                    and draft.preferred_creative_version
                    == latest_creative_version.get("version")
                )
                else ""
            ),
            "creative_preference_notice": (
                request.GET.get("creative_preference")
                if request.GET.get("creative_preference") in {"saved", "stale"}
                else ""
            ),
        },
    )


@login_required
def campaign_report(request, draft_id):
    """Show an honest report shell until verified channel data is available."""

    draft = get_object_or_404(
        WorkspaceCampaignDraft.objects.owned_by(request.user),
        pk=draft_id,
    )
    return render(
        request,
        "campaigns/report.html",
        {
            "draft": draft,
            "report_metrics": (
                "Erişim",
                "Gösterimler",
                "Tıklamalar",
                "Diğer etkileşimler",
                "İletişim talepleri",
                "Medya harcaması",
            ),
        },
    )


@login_required
@require_POST
def campaign_generate_creatives(request, draft_id):
    """Create a provider-free synthetic creative version for the owner."""

    get_object_or_404(
        WorkspaceCampaignDraft.objects.owned_by(request.user),
        pk=draft_id,
    )
    generate_creative_version_for_owner(owner=request.user, draft_id=draft_id)
    return redirect("campaigns:detail", draft_id=draft_id)


@login_required
@require_POST
def campaign_select_preferred_creative(request, draft_id):
    """Record the owner's informational preference for one current variant."""

    draft = get_object_or_404(
        WorkspaceCampaignDraft.objects.owned_by(request.user),
        pk=draft_id,
    )
    try:
        version_number = int(request.POST.get("version", ""))
    except (TypeError, ValueError):
        return redirect(
            f"{reverse('campaigns:detail', args=[draft_id])}?creative_preference=stale"
        )
    result = "saved"
    try:
        select_preferred_creative_for_owner(
            owner=request.user,
            draft_id=draft_id,
            version_number=version_number,
            key=request.POST.get("variant_key", ""),
        )
    except ValidationError:
        result = "stale"
    return redirect(
        f"{reverse('campaigns:detail', args=[draft.pk])}?creative_preference={result}"
    )


@login_required
def campaign_edit(request, draft_id):
    """Change only bounded synthetic budget and duration options."""

    draft = get_object_or_404(
        WorkspaceCampaignDraft.objects.owned_by(request.user),
        pk=draft_id,
    )
    initial_duration = (
        (draft.flight_end - draft.flight_start).days
        if draft.flight_start and draft.flight_end
        else 14
    )
    form = CampaignDraftEditForm(
        request.POST or None,
        initial={
            "media_budget_minor": str(draft.media_budget_minor),
            "duration_days": str(initial_duration),
            "synthetic_confirmation": True,
        },
    )
    if request.method == "POST" and form.is_valid():
        today = timezone.localdate()
        update_campaign_draft_for_owner(
            owner=request.user,
            draft_id=draft.pk,
            media_budget_minor=int(form.cleaned_data["media_budget_minor"]),
            flight_start=today + timedelta(days=1),
            flight_end=today
            + timedelta(days=1 + int(form.cleaned_data["duration_days"])),
        )
        return redirect("campaigns:detail", draft_id=draft.pk)

    return render(
        request,
        "campaigns/edit.html",
        {"draft": draft, "form": form},
    )


@login_required
@require_POST
def campaign_delete(request, draft_id):
    """Remove only the authenticated owner's draft, and only on POST."""

    draft = get_object_or_404(
        WorkspaceCampaignDraft.objects.owned_by(request.user),
        pk=draft_id,
    )
    if request.POST.get("confirm_delete") != "on":
        return redirect("campaigns:detail", draft_id=draft.pk)
    draft.delete()
    return redirect("campaigns:list")
