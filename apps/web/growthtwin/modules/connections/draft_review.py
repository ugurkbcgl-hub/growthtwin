"""Owner-only local review of a frozen workspace-to-Google test package."""

import json
from decimal import Decimal

from django.core import signing
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.middleware.csrf import get_token
from django.utils.html import format_html, format_html_join
from django.views.decorators.csrf import csrf_protect

from growthtwin.modules.campaigns.google_draft_payload import build_draft_package
from growthtwin.modules.campaigns.models import (
    GoogleDraftApproval,
    GoogleDraftDispatch,
    WorkspaceCampaignDraft,
)

from . import backend, draft_dispatch, verification
from .views import local_owner_only

SALT = "local-google-draft-test-review-v1"


@local_owner_only("GET")
def dispatch_status(request, binding):
    try:
        draft = _draft(request, binding)
    except (WorkspaceCampaignDraft.DoesNotExist, ValidationError):
        return HttpResponse("Taslak bulunamadı.", status=404)
    row = GoogleDraftDispatch.objects.filter(draft=draft).first()
    return HttpResponse(
        format_html(
            "<h1>Google test gönderimi</h1><p>{}</p><p>Bu sayfa güncel taslak değişmiş olsa da kayıtlı testi kontrol edip durdurabilir.</p>"
            '<form method="post" action="/connections/google/draft-dispatch/">'
            '<input type="hidden" name="csrfmiddlewaretoken" value="{}"><input type="hidden" name="draft" value="{}">'
            '<button name="action" value="read">Kontrol et</button><button name="action" value="stop">Durdur ve doğrula</button></form>',
            row.state if row else "Henüz gönderilmedi",
            get_token(request),
            draft.pk,
        )
    )


def _draft(request, binding, *, lock=False):
    try:
        draft_id = int(
            request.POST.get("draft")
            if request.method == "POST"
            else request.GET.get("draft")
        )
    except (TypeError, ValueError):
        raise ValidationError("Taslak bulunamadı.") from None
    drafts = WorkspaceCampaignDraft.objects.owned_by(request.user).filter(
        workspace_id=binding[1]
    )
    if lock:
        drafts = drafts.select_for_update()
    return drafts.get(pk=draft_id)


@local_owner_only("GET")
def review(request, binding):
    try:
        draft = _draft(request, binding)
        package = build_draft_package(draft)
        target_key = verification.configuration_key(binding)
    except WorkspaceCampaignDraft.DoesNotExist:
        return HttpResponse("Taslak bulunamadı.", status=404)
    except ValidationError:
        return HttpResponse(
            "Önce güncel reklam metnini seçip kampanya planını tamamlayın.", status=409
        )
    except backend.ConnectionUnavailable:
        return HttpResponse(
            "Önce yerel Google test bağlantısını yapılandırın.", status=409
        )
    payload = json.loads(package.payload_json)
    google = payload["google"]
    approved = GoogleDraftApproval.objects.filter(
        draft=draft, fingerprint=package.fingerprint, target_key=target_key
    ).exists()
    token = signing.dumps(
        {
            "owner": binding[0],
            "workspace": binding[1],
            "draft": draft.pk,
            "fingerprint": package.fingerprint,
            "target_key": target_key,
        },
        salt=SALT,
    )
    assets = format_html_join(
        "",
        "<li>{}</li>",
        ((text,) for text in google["headlines"] + google["descriptions"]),
    )
    dispatch_form = ""
    try:
        plan = draft_dispatch.profile(package)
        dispatch_token = signing.dumps(
            {
                "owner": binding[0],
                "workspace": binding[1],
                "draft": draft.pk,
                "target_key": target_key,
                "dispatch_key": draft_dispatch.review_key(package),
            },
            salt=SALT + "-dispatch",
        )
        row = GoogleDraftDispatch.objects.filter(draft=draft).first()
        dispatch_form = (
            format_html(
                "<h2>Duraklatılmış test gönderimi</h2><p>Özgün adres: {}. TEST adresi açıkça {} olarak değişir; bu bir reklamveren sayfası veya doğrulanmış hizmet değildir.</p>"
                "<p>Günlük sanal bütçe: {} TRY. Başlangıç: {} 00:00:00; bitiş dahil: {} 23:59:59 (Türkiye saat dilimi, hesapta doğrulanır). Ankara / Türkiye şehir kaydı Google’dan tekil ve etkin olarak doğrulanır; konum seçimi PRESENCE.</p>"
                "<p>Günlük bütçe toplam planın gün sayısına (iki uç dahil) bölünüp kuruşa aşağı yuvarlanmasıdır; toplam harcama garantisi değildir. "
                "Anahtar kelime yalnızca “growthtwin synthetic test” / EXACT. Tüm reklam kaynakları PAUSED oluşturulur. Canlı yayın ve medya harcaması yoktur.</p>"
                '<p>Gönderim durumu: {}</p><form method="post" action="/connections/google/draft-dispatch/">'
                '<input type="hidden" name="csrfmiddlewaretoken" value="{}"><input type="hidden" name="draft" value="{}">'
                '<input type="hidden" name="review" value="{}">'
                '<label><input type="checkbox" name="confirm" value="yes"> Yukarıdaki adres ve test ayarlarıyla, onaylı sürümü Google TEST hesabına duraklatılmış göndermeyi onaylıyorum.</label>'
                '<button name="action" value="create">Onaylı sürümü test hesabına gönder</button>'
                '<button name="action" value="read">Gönderilen testi kontrol et</button>'
                '<button name="action" value="stop">Testi durdur ve doğrula</button></form>',
                plan["original_url"],
                plan["test_url"],
                Decimal(plan["daily_micros"]) / 1000000,
                plan["start"],
                plan["end"],
                row.state if row else "Henüz gönderilmedi",
                get_token(request),
                draft.pk,
                dispatch_token,
            )
            if approved
            else ""
        )
    except ValidationError:
        dispatch_form = "Gönderim için ileri tarihli Ankara test planı gerekli."
    return HttpResponse(
        format_html(
            '<!doctype html><html lang="tr"><meta charset="utf-8"><title>Google test gönderimi inceleme</title>'
            "<h1>Google test gönderimi inceleme</h1><p>Bu adım Google’a istek göndermez. Onay yalnızca daha sonra yapılacak duraklatılmış test gönderimi içindir.</p>"
            "<h2>{}</h2><p>Hedef adres: {}</p><p>Toplam örnek plan bütçesi: {} {}. Tarihler: {} – {}. Şehir: {}</p>"
            "<h2>Google için hazırlanan metinler</h2><ul>{}</ul>"
            "<p>Bu metinlerin bazıları karakter sınırına göre kısaltılmış olabilir. Kaynak ve dönüşüm ayrıntıları aşağıdaki tam pakette görünür. "
            "Bu önizleme Google kabulü, hedefleme veya harcama limiti doğrulaması değildir.</p>"
            "<details><summary>Tam sürüm paketini gör</summary><pre>{}</pre></details>"
            '<p>{}</p><form method="post" action="/connections/google/draft-approve/">'
            '<input type="hidden" name="csrfmiddlewaretoken" value="{}">'
            '<input type="hidden" name="draft" value="{}"><input type="hidden" name="review" value="{}">'
            '<label><input type="checkbox" name="confirm" value="yes" required> Bu sürümü yalnızca duraklatılmış Google test gönderimi için onaylıyorum.</label>'
            "<button>Bu test sürümünü onayla</button></form>{}</html>",
            draft.name,
            google["final_url"],
            Decimal(google["media_budget_minor"]) / 100,
            google["currency"],
            google["start"],
            google["end"],
            google["target_city"],
            assets,
            json.dumps(payload, ensure_ascii=False, indent=2),
            "Bu güncel sürümün onayı kayıtlı."
            if approved
            else "Bu güncel sürüm henüz onaylanmadı.",
            get_token(request),
            draft.pk,
            token,
            dispatch_form,
        )
    )


@local_owner_only("POST")
@csrf_protect
def dispatch(request, binding):
    try:
        draft = _draft(request, binding)
        action = request.POST.get("action")
        consent_key = ""
        if action == "create":
            package = build_draft_package(draft)
            target_key = verification.configuration_key(binding)
            consent_key = draft_dispatch.review_key(package)
            token = signing.loads(
                request.POST.get("review", ""), salt=SALT + "-dispatch", max_age=600
            )
            if request.POST.get("confirm") != "yes" or token != {
                "owner": binding[0],
                "workspace": binding[1],
                "draft": draft.pk,
                "target_key": target_key,
                "dispatch_key": consent_key,
            }:
                raise ValidationError("Gönderim onayı güncel değil.")
        row = draft_dispatch.perform(binding, draft.pk, action, consent_key)
        return HttpResponse(
            format_html(
                '<p>Test gönderimi: {}. {}</p><a href="/connections/google/draft-review/?draft={}">İncelemeye dön</a>',
                row.state,
                "Sonuç belirsiz; tekrar oluşturulmaz. Kontrol et veya durdur."
                if row.state == "uncertain"
                else "Google durumu PAUSED olarak doğrulandı.",
                draft.pk,
            ),
            status=409 if row.state == "uncertain" else 200,
        )
    except WorkspaceCampaignDraft.DoesNotExist:
        return HttpResponse("Taslak bulunamadı.", status=404)
    except (
        signing.BadSignature,
        ValidationError,
        GoogleDraftApproval.DoesNotExist,
        backend.ConnectionUnavailable,
        TypeError,
        ValueError,
    ):
        return HttpResponse(
            "Gönderim tamamlanamadı. Güncel onayı, test planını ve bağlantıyı kontrol edin; mevcut işlem yeniden oluşturulmaz.",
            status=409,
        )


@local_owner_only("POST")
@csrf_protect
def approve(request, binding):
    try:
        if request.POST.get("confirm") != "yes":
            raise ValidationError("Açık test onayı gerekli.")
        review = signing.loads(request.POST.get("review", ""), salt=SALT, max_age=600)
        with transaction.atomic():
            draft = _draft(request, binding, lock=True)
            package = build_draft_package(draft)
            target_key = verification.configuration_key(binding)
            if review != {
                "owner": binding[0],
                "workspace": binding[1],
                "draft": draft.pk,
                "fingerprint": package.fingerprint,
                "target_key": target_key,
            }:
                raise ValidationError("Taslak değişti.")
            GoogleDraftApproval.objects.get_or_create(
                draft=draft,
                fingerprint=package.fingerprint,
                target_key=target_key,
                defaults={"payload_json": package.payload_json},
            )
        return HttpResponseRedirect(
            f"/connections/google/draft-review/?draft={draft.pk}"
        )
    except WorkspaceCampaignDraft.DoesNotExist:
        return HttpResponse("Taslak bulunamadı.", status=404)
    except (
        signing.BadSignature,
        ValidationError,
        TypeError,
        ValueError,
        backend.ConnectionUnavailable,
    ):
        return HttpResponse(
            "İnceleme süresi dolmuş, taslak değişmiş veya onay eksik. Güncel paketi yeniden açın.",
            status=409,
        )
