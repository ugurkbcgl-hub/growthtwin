"""Read-only owner journey projection; never authorization or provider evidence."""

from dataclasses import dataclass

from django.conf import settings
from django.urls import reverse

from .exports import preferred_current_variant
from .models import GoogleDraftApproval, GoogleDraftDispatch
from .planning import build_google_search_campaign_plan


def google_test_controls_available(request, draft):
    """Link visibility only, mirroring the existing loopback endpoint boundary.

    Does not read a grant, verify a target or authorize a later operation.
    """
    return bool(
        settings.GOOGLE_ADS_LOCAL_OAUTH_ENABLED
        and not settings.DEBUG
        and request.user.is_authenticated
        and request.user.is_active
        and str(request.user.pk) == str(settings.GOOGLE_ADS_LOCAL_OWNER_ID)
        and str(draft.workspace_id) == str(settings.GOOGLE_ADS_LOCAL_WORKSPACE_ID)
        and request.get_host() == "127.0.0.1:8002"
        and request.META.get("REMOTE_ADDR") == "127.0.0.1"
        and not any(
            key == "HTTP_FORWARDED" or key.startswith("HTTP_X_FORWARDED")
            for key in request.META
        )
    )


@dataclass(frozen=True)
class JourneyStage:
    key: str
    title: str
    status: str
    explanation: str
    href: str | None
    action: str
    unavailable_reason: str = ""


def campaign_journey(request, draft):
    """Project scoped local records only. No credentials, network or writes.

    Stored approval existence does not establish current source/target consent.
    Stored dispatch metadata is not refreshed provider evidence or live serving.
    """
    plan = build_google_search_campaign_plan(draft)
    chosen = preferred_current_variant(draft) is not None
    controls = google_test_controls_available(request, draft)
    approved = GoogleDraftApproval.objects.filter(draft=draft).exists()
    dispatch = (
        GoogleDraftDispatch.objects.filter(draft=draft)
        .values("state", "observed_status", "updated_at")
        .first()
    )
    detail = reverse("campaigns:detail", args=[draft.pk])
    review = (
        f"{reverse('google-local-draft-review')}?draft={draft.pk}"
        if controls and chosen and plan.ready_for_review
        else None
    )
    dispatch_url = (
        f"{reverse('google-local-draft-status')}?draft={draft.pk}"
        if controls and dispatch
        else None
    )
    dispatch_label = "Henüz gönderim kaydı yok"
    if dispatch:
        dispatch_label = "Kayıt var · Durum doğrulanmalı"
        if dispatch["state"] == "uncertain":
            dispatch_label = "Kayıtlı sonuç belirsiz"
        elif dispatch["observed_status"] == "PAUSED":
            dispatch_label = {
                "paused": "Kayıtta duraklatıldı (TEST)",
                "stopped": "Kayıtta durduruldu (TEST)",
            }.get(dispatch["state"], dispatch_label)
    stages = (
        JourneyStage(
            "campaign",
            "Kampanya",
            "Taslak kayıtlı",
            "Bu akış sabit sentetik örnek içindir. Gerçek işletme veya müşteri bilgisi girme.",
            reverse("campaigns:edit", args=[draft.pk]),
            "Plan seçeneklerini düzenle",
        ),
        JourneyStage(
            "creative",
            "Reklam metni",
            "Güncel inceleme tercihi kayıtlı"
            if chosen
            else "Güncel metin seçimi gerekli",
            "Metin tercihi yayın onayı değildir. Bilgiler veya metin sürümü değişirse yeniden seçim gerekir.",
            detail + "#creative-variants-title",
            "Metinleri incele ve seç",
        ),
        JourneyStage(
            "plan",
            "Plan ve bütçe",
            "Yerel incelemeye hazır"
            if plan.ready_for_review
            else "Plan bilgileri eksik",
            "Hedef, tarihler ve örnek medya tavanını incele. Bu, harcanmış tutar veya platformda uygulanmış bir sınır değildir.",
            detail + "#plan-summary-title",
            "Planı ve bütçeyi incele",
        ),
        JourneyStage(
            "approval",
            "TEST onayı",
            "Onay kaydı var · Güncelliği kontrol edilmeli"
            if approved
            else "Onay kaydı yok",
            (
                "Kaydın güncel metin, hedef ve hesapla eşleşmesi burada doğrulanmaz. TEST onayı gerçek yayın veya harcama izni değildir."
                if approved
                else "Henüz TEST onayı kaydı yok. Metin seçimi tek başına onay vermez; gerçek yayın ve harcama için ayrıca izin gerekir."
            ),
            review,
            "TEST paketini incele",
            "Önce güncel metni seç ve planı tamamla."
            if controls and not review
            else "",
        ),
        JourneyStage(
            "dispatch",
            "TEST gönderimi",
            dispatch_label,
            (
                "Bu yalnız kayıtlı TEST durumudur; canlı sorgu yapılmadı. Kayıt eski metin/plan sürümüne ait olabilir. Belirsiz işlem yeniden oluşturulmaz."
                if dispatch
                else "Bu taslak için gönderim kaydı yok. TEST gönderimi, gerçek reklam yayını veya harcama izni değildir."
            ),
            dispatch_url,
            "Kayıtlı testi kontrol et / durdur",
            "Önce TEST paketini incele ve ayrı gönderim onayını ver."
            if controls and not dispatch
            else "",
        ),
        JourneyStage(
            "report",
            "Sonuç raporu",
            "Gerçek veri bağlı değil",
            "Erişim, tıklama, talep ve harcama verisi henüz yok. Planlanan dönem, gözlenmiş sonuç yerine geçmez.",
            reverse("campaigns:report", args=[draft.pk]),
            "Rapor ekranını aç",
        ),
    )
    if dispatch:
        next_title = "Önce kayıtlı TEST işlemini kontrol et"
        next_text = "Yeni gönderimden önce mevcut kaydın durumunu doğrula. Bu sayfa platformdan güncel bilgi almadı."
        next_href = dispatch_url or "#dispatch-stage"
        next_action = "Gönderim adımını aç"
    elif not plan.ready_for_review:
        next_title, next_text = (
            "Planın eksiklerini tamamla",
            "Metin seçimi ve TEST onayı öncesinde plan bilgilerini incele.",
        )
        next_href, next_action = (
            reverse("campaigns:edit", args=[draft.pk]),
            "Planı düzenle",
        )
    elif not chosen:
        next_title, next_text = (
            "Güncel reklam metnini seç",
            "Seçim, inceleme için hangi metni kullanacağını belirtir. Reklam yayımlamaz.",
        )
        next_href, next_action = (
            detail + "#creative-variants-title",
            "Metin seçimine geç",
        )
    else:
        next_title, next_text = (
            "Planı ve onay kapsamını incele",
            "Metin seçildi; bütçe, hedef ve tarihler için ayrıca inceleme ve açık onay gerekir.",
        )
        next_href, next_action = (
            review or detail + "#plan-summary-title",
            "TEST paketini incele" if review else "Plan incelemesine geç",
        )
    return {
        "stages": stages,
        "test_controls_available": controls,
        "dispatch_updated_at": dispatch["updated_at"] if dispatch else None,
        "next_title": next_title,
        "next_text": next_text,
        "next_href": next_href,
        "next_action": next_action,
    }
