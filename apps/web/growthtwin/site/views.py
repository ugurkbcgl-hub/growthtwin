"""Public product pages for the local campaign-experience prototype."""

from django.contrib.sessions.models import Session
from django.shortcuts import redirect, render
from django.urls import reverse

from growthtwin.site.forms import CampaignDraftForm
from growthtwin.site.models import CampaignDraft


def home(request):
    """Create a session-scoped synthetic draft or show its saved preview."""
    form = CampaignDraftForm(
        data=request.POST if request.method == "POST" else None,
    )
    campaign = None

    if request.method == "POST" and form.is_valid():
        if request.session.session_key is None:
            request.session.create()

        session = Session.objects.get(pk=request.session.session_key)
        campaign = CampaignDraft.objects.create(
            session=session,
            brief=form.cleaned_data["brief"],
            daily_limit=form.cleaned_data["daily_limit"],
            duration_days=form.cleaned_data["duration_days"],
        )
        return redirect(f"{reverse('site:home')}?campaign={campaign.pk}")

    if request.method == "GET" and request.GET.get("campaign"):
        try:
            campaign_id = int(request.GET["campaign"])
        except (TypeError, ValueError):
            return redirect("site:home")

        session_key = request.session.session_key
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
                "brief": campaign.brief,
                "daily_limit": campaign.daily_limit,
                "duration_days": campaign.duration_days,
            }
        )

    return render(
        request,
        "site/home.html",
        {"campaign": campaign, "form": form},
    )
