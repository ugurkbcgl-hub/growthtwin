"""Human-readable synthetic review downloads; never platform import payloads."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils import timezone

from growthtwin.modules.campaigns.planning import build_google_search_campaign_plan
from growthtwin.modules.campaigns.services import creative_source_hash_for_draft


def preferred_current_variant(draft):
    """Return only the current, same-source review preference, if present."""

    versions = draft.creative_versions or []
    current = versions[-1] if versions else None
    if (
        not current
        or current.get("source_hash") != creative_source_hash_for_draft(draft)
        or current.get("version") != draft.preferred_creative_version
        or not draft.preferred_creative_key
    ):
        return None
    return next(
        (
            variant
            for variant in current.get("variants", [])
            if variant.get("key") == draft.preferred_creative_key
        ),
        None,
    )


def campaign_review_text(draft, *, version_number, variant_key):
    """Export current plan + selected copy without exposing the rest of history."""

    variant = preferred_current_variant(draft)
    if (
        variant is None
        or version_number != draft.preferred_creative_version
        or variant_key != draft.preferred_creative_key
    ):
        raise ValidationError("Güncel reklam metnini yeniden seçmelisin.")

    plan = build_google_search_campaign_plan(draft)
    generated_at = timezone.now().isoformat(timespec="seconds")
    budget = Decimal(draft.media_budget_minor) / 100
    lines = [
        "GrowthTwin · Sentetik kampanya inceleme dosyası",
        "YAYINLANMADI · GERÇEK REKLAM DEĞİLDİR",
        "Bu dosya inceleme içindir; Google Ads'e aktarılacak bir reklam paketi değildir.",
        "Hesap bağlantısı, yayın onayı, reklam harcaması veya ücret tahsilatı yapılmadı.",
        f"Dosyanın hazırlanma zamanı: {generated_at}",
        "",
        "KAMPANYA PLANI",
        f"Kampanya: {draft.name}",
        f"Marka: {draft.brand_name}",
        "Hedef: Teklif / iletişim talebi",
        f"Kanal adayı: {draft.get_channel_display()}",
        f"Şehir: {draft.target_city}",
        f"Brief: {draft.brief}",
        f"Hedef sayfa: {draft.destination_url or 'Belirtilmedi'}",
        f"Planlanan başlangıç: {draft.flight_start or 'Belirtilmedi'}",
        f"Planlanan bitiş: {draft.flight_end or 'Belirtilmedi'}",
        f"Toplam örnek medya tavanı: {budget:.2f} {draft.currency}",
        "GrowthTwin içerik/hizmet bedelleri bu tutara dahil değildir; hesaplanmadı.",
        "Bu tutar gerçek harcama veya platformda uygulanmış bir limit değildir.",
        "",
        f"TERCİH EDİLEN METİN · Sürüm {version_number}",
        "Bu tercih yalnız inceleme içindir; iddia veya yayın uygunluğu onayı değildir.",
        "Bu metin genel taslaktır; Google Search karakter sınırlarına uyduğu varsayılamaz.",
        f"Başlık: {variant['headline']}",
        f"Metin: {variant['body']}",
        f"Çağrı: {variant['call_to_action']}",
        "",
        "GOOGLE SEARCH İÇİN AYRI BAŞLANGIÇ SEÇENEKLERİ",
        "Aşağıdakiler tercih edilen metinden değil, kampanya bilgilerinden türetilir.",
    ]
    for label, assets in (("Başlık", plan.headlines), ("Açıklama", plan.descriptions)):
        for asset in assets:
            lines.append(
                f"{label} ({len(asset.text)}/{asset.max_characters}): {asset.text}"
            )
    lines.extend(
        [
            "",
            "EKSİKLER VE DOĞRULAMA",
            *plan.missing_requirements,
            f"Sonuç tahmini: {plan.forecast_reason}",
            f"Anahtar kelimeler: {plan.keyword_ideas_reason}",
            "Gerçek işletme bilgileri, iddialar ve hukuk/platform uygunluğu doğrulanmadı.",
            "Gerçek yayın için hesap yetkisi, açık onay ve uygulanabilir harcama sınırları gerekir.",
            "Bu dosya indirildiği anın kopyasıdır; sonraki düzenlemelerle güncellenmez.",
            "",
        ]
    )
    return "\n".join(lines)
