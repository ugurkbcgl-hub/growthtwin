"""Public product pages for the local campaign-experience prototype."""

from uuid import UUID

from django.contrib.sessions.models import Session
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from growthtwin.modules.content.creative import (
    draft_creative_variants,
    source_fingerprint,
)
from growthtwin.modules.content.planning import CampaignBrief, CampaignPlan
from growthtwin.site.forms import CampaignDraftForm, CreativeVariantsForm
from growthtwin.site.models import CampaignDraft


def active_session_key(request):
    """Return the browser session key only while its server record is valid."""
    session_key = request.session.session_key
    if session_key is None:
        return None

    is_active = Session.objects.filter(
        pk=session_key,
        expire_date__gt=timezone.now(),
    ).exists()
    return session_key if is_active else None


@require_POST
def delete_campaign(request, campaign_id):
    """Discard a synthetic draft only from its owning browser session."""
    session_key = active_session_key(request)
    if session_key is None:
        return redirect("site:home")

    CampaignDraft.objects.filter(
        pk=campaign_id,
        session_id=session_key,
    ).delete()
    return redirect("site:home")


def campaign_brief(campaign):
    """Map a session-owned ORM draft into its provider-neutral brief value."""
    return CampaignBrief(
        text=campaign.brief,
        objective=campaign.objective,
        objective_label=campaign.get_objective_display(),
        target_audience=campaign.target_audience,
        brand_context=campaign.brand_context,
    )


def creative_records(campaign, brief):
    """Load saved variants or derive non-persistent examples for older drafts."""
    return campaign.creative_variants or [
        variant.as_record() for variant in draft_creative_variants(brief)
    ]


def render_campaign_home(request, form, campaign, creative_form=None):
    """Render the shared campaign page and its optional creative editor."""
    brief = campaign_brief(campaign) if campaign is not None else None
    plan = (
        CampaignPlan(
            brief=brief,
            daily_limit=campaign.daily_limit,
            duration_days=campaign.duration_days,
        )
        if brief is not None
        else None
    )
    variants = creative_records(campaign, brief) if campaign is not None else []
    if campaign is not None and creative_form is None:
        creative_form = CreativeVariantsForm(variants=variants)
    creative_fields = (
        [
            {
                "variant": variant,
                "headline": creative_form[f"headline_{index}"],
                "body": creative_form[f"body_{index}"],
                "call_to_action": creative_form[f"call_to_action_{index}"],
            }
            for index, variant in enumerate(creative_form.variants)
        ]
        if creative_form is not None
        else []
    )
    creative_is_stale = bool(
        campaign is not None
        and campaign.creative_source_hash
        and campaign.creative_source_hash != source_fingerprint(brief)
    )
    session_key = active_session_key(request)
    drafts = (
        CampaignDraft.objects.filter(session_id=session_key)
        if session_key is not None
        else CampaignDraft.objects.none()
    )
    return render(
        request,
        "site/home.html",
        {
            "campaign": campaign,
            "creative_fields": creative_fields,
            "creative_form": creative_form,
            "creative_is_stale": creative_is_stale,
            "creative_notice": (
                request.GET.get("creative")
                if request.GET.get("creative") in {"saved", "regenerated"}
                else ""
            ),
            "drafts": drafts,
            "form": form,
            "plan": plan,
        },
    )


@require_POST
def save_creatives(request, campaign_id):
    """Save edited synthetic copy only for a draft owned by this session."""
    session_key = active_session_key(request)
    if session_key is None:
        return redirect("site:home")

    campaign = CampaignDraft.objects.filter(
        pk=campaign_id,
        session_id=session_key,
    ).first()
    if campaign is None:
        return redirect("site:home")

    brief = campaign_brief(campaign)
    variants = creative_records(campaign, brief)
    form = CreativeVariantsForm(request.POST, variants=variants)
    if request.POST.get("action") == "regenerate":
        campaign.creative_variants = [
            variant.as_record() for variant in draft_creative_variants(brief)
        ]
        campaign.creative_source_hash = source_fingerprint(brief)
        campaign.save(update_fields=("creative_variants", "creative_source_hash"))
        return redirect(
            f"{reverse('site:home')}?campaign={campaign.pk}&creative=regenerated"
        )

    if form.is_valid():
        campaign.creative_variants = form.cleaned_variants()
        if not campaign.creative_source_hash:
            campaign.creative_source_hash = source_fingerprint(brief)
        campaign.save(update_fields=("creative_variants", "creative_source_hash"))
        return redirect(
            f"{reverse('site:home')}?campaign={campaign.pk}&creative=saved"
        )

    campaign_form = CampaignDraftForm(
        initial={
            "campaign_id": campaign.pk,
            "brief": campaign.brief,
            "brand_context": campaign.brand_context,
            "target_audience": campaign.target_audience,
            "objective": campaign.objective,
            "daily_limit": campaign.daily_limit,
            "duration_days": campaign.duration_days,
        }
    )
    return render_campaign_home(request, campaign_form, campaign, creative_form=form)


def home(request):
    """Create a session-scoped synthetic draft or show its saved preview."""
    form = CampaignDraftForm(
        data=request.POST if request.method == "POST" else None,
    )
    campaign = None

    if request.method == "POST" and form.is_valid():
        campaign_id = form.cleaned_data["campaign_id"]
        session_key = active_session_key(request)
        if campaign_id is not None:
            if session_key is None:
                return redirect("site:home")

            campaign = CampaignDraft.objects.filter(
                pk=campaign_id,
                session_id=session_key,
            ).first()
            if campaign is None:
                return redirect("site:home")

            campaign.brief = form.cleaned_data["brief"]
            campaign.brand_context = form.cleaned_data["brand_context"]
            campaign.target_audience = form.cleaned_data["target_audience"]
            campaign.objective = form.cleaned_data["objective"]
            campaign.daily_limit = form.cleaned_data["daily_limit"]
            campaign.duration_days = form.cleaned_data["duration_days"]
            campaign.save(
                update_fields=(
                    "brief",
                    "brand_context",
                    "target_audience",
                    "objective",
                    "daily_limit",
                    "duration_days",
                )
            )
        else:
            if session_key is None:
                request.session.create()
                session_key = request.session.session_key

            session = Session.objects.get(pk=session_key)
            campaign = CampaignDraft.objects.create(
                session=session,
                brief=form.cleaned_data["brief"],
                brand_context=form.cleaned_data["brand_context"],
                target_audience=form.cleaned_data["target_audience"],
                objective=form.cleaned_data["objective"],
                daily_limit=form.cleaned_data["daily_limit"],
                duration_days=form.cleaned_data["duration_days"],
            )
            brief = campaign_brief(campaign)
            campaign.creative_variants = [
                variant.as_record() for variant in draft_creative_variants(brief)
            ]
            campaign.creative_source_hash = source_fingerprint(brief)
            campaign.save(update_fields=("creative_variants", "creative_source_hash"))
        return redirect(f"{reverse('site:home')}?campaign={campaign.pk}")

    if request.method == "GET" and request.GET.get("campaign"):
        try:
            campaign_id = UUID(request.GET["campaign"])
        except (TypeError, ValueError):
            return redirect("site:home")

        session_key = active_session_key(request)
        if session_key is None:
            return redirect("site:home")

        campaign = CampaignDraft.objects.filter(
            pk=campaign_id,
            session_id=session_key,
        ).first()
        if campaign is None:
            return redirect("site:home")

        form = CampaignDraftForm(
            initial={
                "campaign_id": campaign.pk,
                "brief": campaign.brief,
                "brand_context": campaign.brand_context,
                "target_audience": campaign.target_audience,
                "objective": campaign.objective,
                "daily_limit": campaign.daily_limit,
                "duration_days": campaign.duration_days,
            }
        )

    return render_campaign_home(request, form, campaign)
