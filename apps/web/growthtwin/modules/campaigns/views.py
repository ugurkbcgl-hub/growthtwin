"""Authenticated views for local synthetic campaign planning."""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.formats import number_format

from growthtwin.modules.campaigns.forms import CampaignDraftForm
from growthtwin.modules.campaigns.models import WorkspaceCampaignDraft
from growthtwin.modules.campaigns.planning import build_google_search_campaign_plan
from growthtwin.modules.campaigns.services import create_campaign_draft_for_owner
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
    return render(
        request,
        "campaigns/detail.html",
        {
            "draft": draft,
            "plan": build_google_search_campaign_plan(draft),
            "budget_display": _format_budget(draft.media_budget_minor),
        },
    )
