"""Owner-only local review of a frozen workspace-to-Google test package."""

import json
from decimal import Decimal

from django.core import signing
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django.views.decorators.csrf import csrf_protect

from growthtwin.modules.campaigns.google_draft_payload import build_draft_package
from growthtwin.modules.campaigns.journey import stored_test_dispatch_label
from growthtwin.modules.campaigns.models import (
    GoogleDraftApproval,
    GoogleDraftDispatch,
    WorkspaceCampaignDraft,
)

from . import backend, draft_dispatch, total_budget, verification
from .views import local_owner_only

SALT = "local-google-draft-test-review-v1"


def _page(request, draft, body, *, title, status=200):
    """Presentation only; callers keep the existing local owner/action guards."""
    return render(
        request,
        "connections/draft_test.html",
        {"draft": draft, "body": body, "page_title": title},
        status=status,
    )


def _problem(request, draft, message):
    # Never add campaign links until an owned draft was successfully resolved.
    if draft is None:
        return HttpResponse(message, status=409)
    return _page(
        request,
        draft,
        format_html(
            "<h1>İşlem tamamlanamadı</h1><p>{}</p><p>Güncel metni, planı ve TEST onayını incele. Bu uyarı tek başına kayıtlı TEST işleminin durumunu veya durduğunu doğrulamaz.</p>",
            message,
        ),
        title="TEST işlemi için kontrol gerekli",
        status=409,
    )


@local_owner_only("GET")
def dispatch_status(request, binding):
    try:
        draft = _draft(request, binding)
    except (WorkspaceCampaignDraft.DoesNotExist, ValidationError):
        return HttpResponse("Taslak bulunamadı.", status=404)
    row = (
        GoogleDraftDispatch.objects.filter(draft=draft)
        .values("state", "observed_status", "updated_at")
        .first()
    )
    controls = ""
    if row:
        controls = format_html(
            "<p>Kontrol et Google TEST hesabından güncel durumu ister. Durdur ve doğrula kayıtlı TEST kampanyasını duraklatmayı ister; sonuç belirsiz kalabilir. Bu işlemler sayfa açılınca çalışmaz.</p>"
            '<form method="post" action="/connections/google/draft-dispatch/">'
            '<input type="hidden" name="csrfmiddlewaretoken" value="{}"><input type="hidden" name="draft" value="{}">'
            '<button name="action" value="read">Kontrol et</button><button name="action" value="stop">Durdur ve doğrula</button></form>',
            get_token(request),
            draft.pk,
        )
    body = format_html(
        '<h1>Kayıtlı TEST gönderimi</h1><p class="status-tag">{}</p>'
        "<p>Bu sayfa yalnız yerel kaydı gösterir; Google’a istek gönderilmedi. Kayıt eski metin/plan sürümüne ait olabilir; gerçek yayın veya harcama kanıtı değildir.</p>"
        "<p>Yerel kaydın güncellenme zamanı: {}. Bu, platform verisinin tazeliğini kanıtlamaz.</p>"
        "<p>Güncel taslak değişmiş olsa da mevcut kayıt kontrol edilip durdurulabilir. Belirsiz sonuçta yeniden gönderim oluşturulmaz.</p>{}",
        stored_test_dispatch_label(row),
        timezone.localtime(row["updated_at"]).strftime("%d.%m.%Y %H:%M %z")
        if row
        else "Henüz kayıt yok",
        controls,
    )
    return _page(request, draft, body, title="Kayıtlı TEST gönderimi")


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
    draft = None
    try:
        draft = _draft(request, binding)
        package = build_draft_package(draft)
        target_key = verification.configuration_key(binding)
    except WorkspaceCampaignDraft.DoesNotExist:
        return HttpResponse("Taslak bulunamadı.", status=404)
    except ValidationError:
        return _problem(
            request,
            draft,
            "Önce güncel reklam metnini seçip kampanya planını tamamlayın.",
        )
    except backend.ConnectionUnavailable:
        return _problem(
            request, draft, "Önce yerel Google test bağlantısını yapılandırın."
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
        stored_note = "Henüz gönderim kaydı yok."
        legacy = False
        if row:
            stored_profile = json.loads(row.payload_json)["test_profile"]
            stored_period, _, stored_amount, _ = draft_dispatch.budget_spec(
                stored_profile
            )
            legacy = stored_period == "DAILY"
            stored_note = format_html(
                "Kayıtlı test bütçesi: {} TRY / {}. {}",
                Decimal(stored_amount) / 1000000,
                "günlük ortalama" if legacy else "kampanya toplamı",
                "Bu günlük kayıt korunur. Toplam bütçeli test için çalışma alanından yeni sentetik taslak oluşturun."
                if legacy
                else "Tekrar gönderme yeni bir test oluşturmaz.",
            )
        create_button = format_html(
            '<button name="action" value="create" {}>Onaylı sürümü toplam bütçeli test hesabına gönder</button>',
            "disabled" if legacy else "",
        )
        dispatch_form = (
            format_html(
                "<h2>Toplam bütçeli duraklatılmış test</h2><p>Özgün adres: {}. TEST adresi açıkça {} olarak değişir; bu bir reklamveren sayfası veya doğrulanmış hizmet değildir.</p>"
                "<p>Yeni test için toplam sanal bütçe: {} TRY. Başlangıç: {} 00:00:00; bitiş dahil: {} 23:59:59 (Türkiye saat dilimi, hesapta doğrulanır). Ankara / Türkiye şehir kaydı Google’dan tekil ve etkin olarak doğrulanır; konum seçimi PRESENCE.</p>"
                "<p>Yeni test paylaşılmayan CUSTOM_PERIOD toplam bütçesi kullanır; günlük bütçeye otomatik geçilmez. Bu test gerçek harcama veya hesap genelindeki sınırların kanıtı değildir. "
                "Anahtar kelime yalnızca “growthtwin synthetic test” / EXACT. Tüm reklam kaynakları PAUSED oluşturulur. Canlı yayın ve medya harcaması yoktur.</p>"
                '<p>{}</p><p>Kayıtlı gönderim durumu (canlı sorgu değil): {}</p><form method="post" action="/connections/google/draft-dispatch/">'
                '<input type="hidden" name="csrfmiddlewaretoken" value="{}"><input type="hidden" name="draft" value="{}">'
                '<input type="hidden" name="review" value="{}">'
                '<label><input type="checkbox" name="confirm" value="yes"> Yukarıdaki adres, kesin toplam bütçe ve tarihlerle onaylı sürümü yalnız Google TEST hesabına duraklatılmış göndermeyi onaylıyorum.</label>{}'
                '<button name="action" value="read">Gönderilen testi kontrol et</button>'
                '<button name="action" value="stop">Testi durdur ve doğrula</button></form>',
                plan["original_url"],
                plan["test_url"],
                Decimal(plan["total_micros"]) / 1000000,
                plan["start"],
                plan["end"],
                stored_note,
                stored_test_dispatch_label(
                    {"state": row.state, "observed_status": row.observed_status}
                    if row
                    else None
                ),
                get_token(request),
                draft.pk,
                dispatch_token,
                create_button,
            )
            if approved
            else ""
        )
    except ValidationError:
        dispatch_form = "Gönderim için ileri tarihli Ankara test planı gerekli."
    budget_form = ""
    if approved:
        try:
            budget_plan = total_budget.plan(package)
            budget_token = signing.dumps(
                {
                    "owner": binding[0],
                    "workspace": binding[1],
                    "draft": draft.pk,
                    "target_key": target_key,
                    "budget_key": total_budget.review_key(package),
                },
                salt=SALT + "-total-budget",
            )
            budget_form = format_html(
                "<h2>Toplam bütçe için gönderimsiz test</h2><p>Kampanya toplamı: {} TRY. {} 00:00:00 – {} 23:59:59, Türkiye saat dilimi.</p>"
                "<p>Bu kontrol, yukarıdaki örnek adres, konum ve reklam metniyle yalnızca Google TEST hesabında istek doğrulaması yapar. "
                "Reklam oluşturmaz ve mevcut testlerin bütçe ayarlarını değiştirmez. "
                "Başarılı sonuç gerçek yayın veya harcama izni değildir.</p>"
                '<form method="post" action="/connections/google/total-budget-validate/">'
                '<input type="hidden" name="csrfmiddlewaretoken" value="{}"><input type="hidden" name="draft" value="{}">'
                '<input type="hidden" name="review" value="{}"><button>Toplam bütçeli isteği TEST hesabında doğrula</button></form>',
                Decimal(budget_plan["total_micros"]) / 1000000,
                budget_plan["start"],
                budget_plan["end"],
                get_token(request),
                draft.pk,
                budget_token,
            )
        except ValidationError:
            pass
    return _page(
        request,
        draft,
        format_html(
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
            "<button>Bu test sürümünü onayla</button></form>{}{}",
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
            budget_form,
        ),
        title="Google TEST paketi inceleme",
    )


@local_owner_only("POST")
@csrf_protect
def validate_total_budget(request, binding):
    draft = None
    try:
        draft = _draft(request, binding)
        package = build_draft_package(draft)
        key = total_budget.review_key(package)
        token = signing.loads(
            request.POST.get("review", ""), salt=SALT + "-total-budget", max_age=600
        )
        if token != {
            "owner": binding[0],
            "workspace": binding[1],
            "draft": draft.pk,
            "target_key": verification.configuration_key(binding),
            "budget_key": key,
        }:
            raise ValidationError("Budget review changed.")
        result = total_budget.validate(binding, draft.pk, key)
        return _page(
            request,
            draft,
            format_html(
                "<h1>Toplam bütçe isteği doğrulandı</h1><p>Google TEST hesabı {} TRY toplam bütçeli isteği kabul etti. "
                "Yalnızca istek doğrulaması yapıldı: yeni reklam veya bütçe oluşturulmadı; mevcut test değişmedi.</p>"
                "<p>Bu sonuç gerçek harcama sınırının çalıştığını, reklamın yayınlanabileceğini veya hesabın üretime hazır olduğunu kanıtlamaz.</p>"
                '<a href="/connections/google/draft-review/?draft={}">Taslağa dön</a>',
                Decimal(result["total_micros"]) / 1000000,
                draft.pk,
            ),
            title="Toplam bütçe TEST doğrulaması",
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
        return _problem(
            request,
            draft,
            "Toplam bütçe isteği doğrulanamadı. Güncel onayı ve test bağlantısını kontrol edin. Günlük bütçeye otomatik geçilmedi ve yeni reklam oluşturulmadı.",
        )


@local_owner_only("POST")
@csrf_protect
def dispatch(request, binding):
    draft = None
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
        stored_profile = json.loads(row.payload_json)["test_profile"]
        period, _, amount, _ = draft_dispatch.budget_spec(stored_profile)
        return _page(
            request,
            draft,
            format_html(
                "<h1>Google TEST işlem sonucu</h1><p>Test gönderimi: {}. {}</p><p>Kayıtlı bütçe: {} TRY / {}. Dönem: {} – {}.</p>"
                '<p>Sonuç yalnız TEST hesabı içindir; gerçek reklam yayını ve harcama yoktur.</p><a href="/connections/google/draft-review/?draft={}">İncelemeye dön</a>',
                stored_test_dispatch_label(
                    {"state": row.state, "observed_status": row.observed_status}
                ),
                "Sonuç belirsiz; tekrar oluşturulmaz. Kontrol et veya durdur."
                if row.state == "uncertain"
                else (
                    "Bu işlemde Google TEST hesabından PAUSED durumu, bütçe türü/tutarı ve tarihler doğrulandı. Bu gözlem sonucun alındığı ana aittir; gelecekteki durumu veya gerçek yayını kanıtlamaz."
                    if row.state in {"paused", "stopped"}
                    and row.observed_status == "PAUSED"
                    else "Kayıtlı durum doğrulanmalı; başarılı yayın veya harcama sonucu gösterilmiyor."
                ),
                Decimal(amount) / 1000000,
                period,
                stored_profile["start"],
                stored_profile["end"],
                draft.pk,
            ),
            title="Google TEST işlem sonucu",
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
        return _problem(
            request,
            draft,
            "Gönderim tamamlanamadı. Güncel onayı, test planını ve bağlantıyı kontrol edin; mevcut işlem yeniden oluşturulmaz.",
        )


@local_owner_only("POST")
@csrf_protect
def approve(request, binding):
    draft = None
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
        return _problem(
            request,
            draft,
            "İnceleme süresi dolmuş, taslak değişmiş veya onay eksik. Güncel paketi yeniden açın.",
        )
