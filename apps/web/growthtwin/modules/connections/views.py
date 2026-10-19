"""Explicitly enabled, owner-bound loopback OAuth setup; never publishes ads."""

import time
from functools import wraps

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.middleware.csrf import get_token
from django.utils.html import format_html
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_variables

from growthtwin.modules.campaigns.models import GoogleTestCampaign
from growthtwin.modules.workspaces.models import Workspace
from growthtwin.modules.workspaces.services import get_workspace_for_owner

from . import backend, verification
from .google_oauth import AuthorizationRejected, LocalAuthorizationStore

authorization_store = LocalAuthorizationStore()
STATUS_PATH = "/connections/google/"


def local_owner_only(method):
    def decorate(view):
        @wraps(view)
        @sensitive_variables()
        def guarded(request):
            response = HttpResponse("Yerel bağlantı kullanılamıyor.", status=404)
            try:
                enabled = getattr(settings, "GOOGLE_ADS_LOCAL_OAUTH_ENABLED", False)
                owner_id = str(getattr(settings, "GOOGLE_ADS_LOCAL_OWNER_ID", ""))
                workspace_id = str(
                    getattr(settings, "GOOGLE_ADS_LOCAL_WORKSPACE_ID", "")
                )
                allowed = (
                    enabled
                    and not settings.DEBUG
                    and request.get_host() == "127.0.0.1:8002"
                    and request.META.get("REMOTE_ADDR") == "127.0.0.1"
                    and not any(
                        key == "HTTP_FORWARDED" or key.startswith("HTTP_X_FORWARDED")
                        for key in request.META
                    )
                    and owner_id
                    and workspace_id
                    and request.user.is_authenticated
                    and str(request.user.pk) == owner_id
                )
                if allowed:
                    workspace = get_workspace_for_owner(
                        owner=request.user, workspace_id=workspace_id
                    )
                    if request.method != method:
                        response = HttpResponse(status=405)
                        response["Allow"] = method
                    else:
                        if not request.session.session_key:
                            request.session.create()
                        binding = (
                            owner_id,
                            str(workspace.pk),
                            request.session.session_key,
                        )
                        response = view(request, binding)
            except (Workspace.DoesNotExist, PermissionDenied, ValueError):
                pass
            except Exception:
                # Neither raw provider exceptions nor callback-bearing debug
                # pages may escape this isolated credential flow.
                response = HttpResponse("Bağlantı kontrolü tamamlanamadı.", status=503)
            response["Cache-Control"] = "no-store"
            response["Referrer-Policy"] = "no-referrer"
            return response

        return guarded

    return decorate


@local_owner_only("GET")
@sensitive_variables()
def status(request, binding):
    saved = backend.connection_exists(binding)
    evidence = request.session.get("google_test_verification", {})
    verified = False
    try:
        age = time.time() - evidence["at"]
        verified = (
            saved
            and 0 <= age < 600
            and evidence["key"] == verification.configuration_key(binding)
        )
    except (KeyError, TypeError, backend.ConnectionUnavailable):
        pass
    if not verified:
        request.session.pop("google_test_verification", None)
    test_row = (
        GoogleTestCampaign.objects.filter(workspace_id=binding[1]).first()
        if getattr(settings, "GOOGLE_ADS_LOCAL_TEST_CAMPAIGN_ENABLED", False)
        else None
    )
    test_states = {
        "uncertain": "Sonuç belirsiz; tekrar oluşturulmaz. Durumu oku.",
        "paused": "Google test kampanyası duraklatılmış durumda.",
        "stopped": "Durdurma doğrulandı; Google durumu duraklatılmış.",
        "attention": "Google durumu kontrol edilmeli.",
    }
    test_html = ""
    if getattr(settings, "GOOGLE_ADS_LOCAL_TEST_CAMPAIGN_ENABLED", False):
        test_html = format_html(
            "<section><h2>Google test kampanyası</h2>"
            "<p>Sabit sentetik Search reklamı, örnek adres example.com. "
            "Test hesabı reklam göstermez; gerçek para harcanmaz. "
            "Sanal günlük bütçe: hesap para biriminde 1. "
            "Kampanya, reklam grubu ve reklam duraklatılmış oluşturulur.</p>"
            "<p>{}</p><p>Son Google durumu: {}</p>"
            '<form method="post" action="/connections/google/test-campaign/">'
            '<input type="hidden" name="csrfmiddlewaretoken" value="{}">'
            '<button name="action" value="create">Duraklatılmış test kampanyası oluştur</button> '
            '<button name="action" value="read">Test kampanyası durumunu oku</button> '
            '<button name="action" value="stop">Test kampanyasını durdur</button>'
            "</form><p>Her çalışma alanında tek test işlemi bulunur. "
            "Belirsiz sonuçta oluşturma yeniden gönderilmez.</p></section>",
            test_states.get(test_row.state, "İşlem kaydı var; durumunu oku.")
            if test_row
            else "Henüz test kampanyası oluşturulmadı.",
            test_row.observed_status
            if test_row and test_row.observed_status
            else "Henüz okunmadı",
            get_token(request),
        )
    message = request.session.pop("google_local_result", "")
    diagnosis = request.session.get("google_local_diagnostic", "")
    diagnoses = {
        "state": "Bağlantı denemesi süresi dolmuş, oturum değişmiş veya Google izin dönüşü geçersiz. Yeni deneme gerekir.",
        "network": "Google izin sunucusuna erişilemedi.",
        "google_rejected": "Google izin değişimini reddetti.",
        "invalid_client": "Google uygulama kimliğini veya anahtarını kabul etmedi.",
        "invalid_grant": "Google geçici yetki kodunu kabul etmedi.",
        "token_shape": "Google yanıtında beklenen izin veya yenileme bilgisi bulunamadı.",
        "storage": "Google yanıtı alındı ancak şifreli kayıt tamamlanamadı.",
        "unavailable": "Yerel bağlantı yapılandırması veya anahtar erişimi kontrol edilmeli.",
        "unexpected": "Yerel bağlantı işlenirken beklenmeyen bir hata oluştu.",
    }
    # Session values never contain provider responses, codes or credentials.
    messages = {
        "saved": "Yetkilendirme şifreli olarak kaydedildi.",
        "failed": (
            "Bağlantı tamamlanamadı. İzin iptali tamamlanamadıysa Google "
            "hesabınızdan GrowthTwin erişimini kaldırabilirsiniz."
        ),
        "exists": "Yetkilendirme zaten kayıtlı. Yeniden bağlanmadan önce kaldırın.",
        "removed": "Yerel yetkilendirme kaldırıldı.",
        "verified": "Google test hesabı kontrolü başarılı.",
        "verification_failed": "Test hesabı doğrulanamadı. Hesap yapılandırmasını veya Google erişimini kontrol edin.",
        "test_campaign_done": "Test kampanyası işlemi tamamlandı; aşağıdaki durumu kontrol edin.",
        "test_campaign_failed": "Test işlemi tamamlanamadı. Yeni kampanya oluşturmadan durumunu okuyun.",
    }
    return HttpResponse(
        format_html(
            '<!doctype html><html lang="tr"><meta charset="utf-8">'
            "<title>Google test bağlantısı</title><h1>Google test bağlantısı</h1>"
            "<p>Yalnızca yerel test içindir. Reklam yayımlamaz.</p>"
            "<p>Google izni yalnızca okuma yetkisi değildir. "
            "Hesap kontrolü yalnızca yapılandırılmış hedefi okur.</p>"
            "<p>{}</p>"
            "<p>{}</p><p>{}</p>"
            '<form method="post" action="/connections/google/verify/">'
            '<input type="hidden" name="csrfmiddlewaretoken" value="{}">'
            "<button>Test hesabı bağlantısını kontrol et</button></form>"
            '<form method="post" action="/connections/google/start/">'
            '<input type="hidden" name="csrfmiddlewaretoken" value="{}">'
            "<button>Google ile yetkilendir</button></form>"
            '<form method="post" action="/connections/google/disconnect/">'
            '<input type="hidden" name="csrfmiddlewaretoken" value="{}">'
            "<button>Yetkilendirmeyi kaldır</button></form>{}</html>",
            "Test hesabı son 10 dakika içinde API ile doğrulandı. Bu kontrol reklam yayınına izin vermez."
            if verified
            else "Güncel test hesabı doğrulaması yok.",
            "Yetkilendirme kaydı mevcut. Yeniden bağlanmadan önce kaldırın."
            if saved
            else "Yetkilendirme kaydı yok.",
            messages.get(message, "") + " " + diagnoses.get(diagnosis, ""),
            get_token(request),
            get_token(request),
            get_token(request),
            test_html,
        )
    )


@local_owner_only("POST")
@csrf_protect
@sensitive_variables()
def start(request, binding):
    request.session.pop("google_local_diagnostic", None)
    try:
        if backend.connection_exists(binding):
            request.session["google_local_result"] = "exists"
            return HttpResponseRedirect(STATUS_PATH)
        url = authorization_store.begin(
            client_id=backend.load_client_id(), binding=binding
        )
        return HttpResponseRedirect(url)
    except (backend.ConnectionUnavailable, AuthorizationRejected):
        request.session["google_local_result"] = "failed"
        return HttpResponseRedirect(STATUS_PATH)


@local_owner_only("GET")
@sensitive_variables()
def callback(request, binding):
    try:
        authorization_code = authorization_store.consume(
            binding=binding, query=request.META.get("QUERY_STRING", "")
        )
        backend.exchange_and_store(authorization_code, binding)
        request.session["google_local_result"] = "saved"
        request.session.pop("google_local_diagnostic", None)
    except AuthorizationRejected:
        request.session["google_local_result"] = "failed"
        request.session["google_local_diagnostic"] = "state"
    except backend.ConnectionUnavailable as error:
        request.session["google_local_result"] = "failed"
        request.session["google_local_diagnostic"] = error.reason
    except Exception:
        # Always remove callback parameters from the browser, even for an
        # unexpected local storage/transport failure. No exception is echoed.
        request.session["google_local_result"] = "failed"
        request.session["google_local_diagnostic"] = "unexpected"
    return HttpResponseRedirect(STATUS_PATH)


@local_owner_only("POST")
@csrf_protect
@sensitive_variables()
def disconnect(request, binding):
    request.session.pop("google_test_verification", None)
    try:
        backend.disconnect(binding)
        request.session["google_local_result"] = "removed"
    except backend.ConnectionUnavailable:
        request.session["google_local_result"] = "failed"
    return HttpResponseRedirect(STATUS_PATH)


@local_owner_only("POST")
@csrf_protect
@sensitive_variables()
def verify_test_account(request, binding):
    request.session.pop("google_test_verification", None)
    try:
        key = verification.verify(binding)
        request.session["google_test_verification"] = {"key": key, "at": time.time()}
        request.session["google_local_result"] = "verified"
    except Exception:
        request.session["google_local_result"] = "verification_failed"
    return HttpResponseRedirect(STATUS_PATH)


@local_owner_only("POST")
@csrf_protect
@sensitive_variables()
def test_campaign_action(request, binding):
    from .test_campaign import perform

    try:
        perform(binding, request.POST.get("action"))
        request.session["google_local_result"] = "test_campaign_done"
    except Exception:
        request.session["google_local_result"] = "test_campaign_failed"
    return HttpResponseRedirect(STATUS_PATH)
