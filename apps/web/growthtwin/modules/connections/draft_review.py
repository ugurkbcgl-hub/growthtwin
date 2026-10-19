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
    WorkspaceCampaignDraft,
)

from . import backend, verification
from .views import local_owner_only

SALT = "local-google-draft-test-review-v1"


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
            "<button>Bu test sürümünü onayla</button></form></html>",
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
        )
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
