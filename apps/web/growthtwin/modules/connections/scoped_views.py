"""Closed-by-default loopback endpoints; mocked validation, no rollout yet."""

import hashlib
import secrets
from functools import wraps
from urllib.parse import parse_qs, urlsplit
from uuid import UUID, uuid4

from django.conf import settings
from django.core import signing
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_variables

from . import backend
from . import scoped_oauth_candidate as candidate
from .candidate_recovery import assess_candidate
from .candidate_retirement import receipt_binding_digest, retire_reserved
from .connector_identity import IdentityConflict, get_identity
from .models import ConnectorIdentity
from .models import ScopedOAuthCandidateAttempt as Attempt
from .views import local_owner_only

STATUS_PATH = "/connections/google/scoped/"
SALT = "growthtwin.scoped-candidate-endpoint.v1"
MARKER = "scoped_candidate_attempt"
NOTICES = {
    "callback_denied": "Dönüş bu oturumdaki denemeyle eşleşmedi. Yeni işlem gönderilmedi.",
    "callback_result": "Dönüş işlendi. Aşağıdaki kayıt bağlantının etkinleştiği anlamına gelmez.",
    "retired": "Gönderim öncesindeki deneme sonlandırıldı. Mevcut Google erişimi değiştirilmedi.",
}
LABELS = {
    "callback_wait": "Yetkilendirme dönüşü bekleniyor.",
    "restart_review": "Oturum veya süre değişmiş. Gönderim öncesindeki deneme sonlandırılabilir.",
    "reconciliation_required": "İşlem sonucu belirsiz. Yeniden gönderilmez; inceleme gerekir.",
    "inactive_candidate_review": "Aday kaydı var. Bağlantı etkin değil ve hesap hedefi henüz doğrulanmadı.",
    "rejected_history": "Deneme kapanmış. Bu kayıt yeni bir yetki sağlamaz.",
}


def _guard(method):
    def decorate(view):
        guarded = local_owner_only(method)(view)

        @wraps(view)
        def wrapped(request):
            if (
                settings.GOOGLE_ADS_SCOPED_ENDPOINTS_ENABLED is not True
                or settings.GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED is not True
            ):
                return HttpResponse("Bağlantı alanı kullanılamıyor.", status=404)
            return guarded(request)

        return wrapped

    return decorate


def _problem(request, code=409):
    return render(
        request,
        "connections/scoped_candidate.html",
        {"problem": True, "configuration_problem": code == 503},
        status=code,
    )


def _ticket(binding, current, action, row=None):
    return signing.dumps(
        {
            "owner": binding[0],
            "workspace": binding[1],
            "session": candidate._session_key(binding[2]),
            "connection": str(current.connection_id),
            "generation": str(row.generation if row else current.generation),
            "revision": row.expected_revision if row else current.revision,
            "attempt": str(row.pk if row else uuid4()),
            "operation": str(uuid4()),
            "receipt": receipt_binding_digest(row) if row else "new",
            "action": action,
        },
        salt=SALT,
    )


@sensitive_variables()
def _submitted(request, binding, action):
    if (
        request.FILES
        or set(request.POST) - {"csrfmiddlewaretoken", "token", "confirm"}
        or request.POST.getlist("confirm") != ["yes"]
        or len(request.POST.getlist("token")) != 1
        or len(request.POST["token"]) > 4096
        or any(len(request.POST.getlist(key)) != 1 for key in request.POST)
    ):
        raise ValueError
    value = signing.loads(request.POST["token"], salt=SALT, max_age=300)
    if (
        type(value) is not dict
        or set(value)
        != {
            "owner",
            "workspace",
            "session",
            "connection",
            "generation",
            "revision",
            "attempt",
            "operation",
            "receipt",
            "action",
        }
        or value["owner"] != binding[0]
        or value["workspace"] != binding[1]
        or value["session"] != candidate._session_key(binding[2])
        or value["action"] != action
        or type(value["revision"]) is not int
        or type(value["receipt"]) is not str
    ):
        raise ValueError
    for key in ("connection", "generation", "attempt", "operation"):
        if (
            type(value[key]) is not str
            or not UUID(value[key]).int
            or str(UUID(value[key])) != value[key]
        ):
            raise ValueError
    return value


@_guard("GET")
@sensitive_variables()
def overview(request, binding):
    context = {
        "notice": NOTICES.get(request.session.get("scoped_candidate_notice"), "")
    }
    connector = ConnectorIdentity.objects.filter(
        workspace_id=binding[1], provider="google_ads_test"
    ).first()
    if connector:
        current = get_identity(
            owner=request.user, workspace_id=binding[1], connection_id=connector.pk
        )
        row = (
            Attempt.objects.filter(connection=connector)
            .order_by("-created_at", "id")
            .first()
        )
        unresolved = (
            Attempt.objects.filter(connection=connector)
            .exclude(state=Attempt.State.REJECTED)
            .exists()
        )
        if current.state == "quarantined" and not unresolved:
            context["start_token"] = _ticket(binding, current, "start")
        if row:
            assessment = assess_candidate(
                owner=request.user,
                workspace_id=binding[1],
                connection_id=connector.pk,
                attempt_id=row.pk,
                session_key=binding[2],
            )
            context["message"] = LABELS[assessment.disposition]
            if (
                row.state == "reserved"
                and assessment.current_scope
                and not Attempt.objects.filter(connection=connector)
                .exclude(pk=row.pk)
                .exclude(state=Attempt.State.REJECTED)
                .exists()
            ):
                context["retire_token"] = _ticket(binding, current, "retire", row)
    return render(request, "connections/scoped_candidate.html", context)


@_guard("POST")
@csrf_protect
@sensitive_variables()
def start(request, binding):
    try:
        value = _submitted(request, binding, "start")
        if value["receipt"] != "new":
            raise ValueError
        result = candidate.begin_candidate(
            owner=request.user,
            workspace_id=binding[1],
            connection_id=UUID(value["connection"]),
            attempt_id=UUID(value["attempt"]),
            expected_generation=UUID(value["generation"]),
            expected_revision=value["revision"],
            session_key=binding[2],
        )
        state = parse_qs(urlsplit(result.authorization_url).query)["state"]
        if len(state) != 1:
            raise ValueError
        request.session[MARKER] = {
            key: value[key]
            for key in ("connection", "generation", "revision", "attempt", "session")
        }
        request.session[MARKER]["state_hash"] = hashlib.sha256(
            state[0].encode("ascii")
        ).hexdigest()
        request.session.pop("scoped_candidate_notice", None)
        return HttpResponseRedirect(result.authorization_url)
    except (signing.BadSignature, ValueError, KeyError, TypeError, IdentityConflict):
        return _problem(request)
    except backend.ConnectionUnavailable:
        return _problem(request, 503)


@_guard("GET")
@sensitive_variables()
def callback(request, binding):
    try:
        marker = request.session.get(MARKER)
        if (
            type(marker) is not dict
            or set(marker)
            != {
                "connection",
                "generation",
                "revision",
                "attempt",
                "session",
                "state_hash",
            }
            or marker["session"] != candidate._session_key(binding[2])
        ):
            raise ValueError
        query = request.META.get("QUERY_STRING", "")
        if len(query) > 8192:
            raise ValueError
        params = parse_qs(query, keep_blank_values=True, max_num_fields=20)
        if len(params.get("state", [])) != 1:
            raise ValueError
        state_hash = hashlib.sha256(params["state"][0].encode("ascii")).hexdigest()
        if type(marker["state_hash"]) is not str or not secrets.compare_digest(
            state_hash, marker["state_hash"]
        ):
            raise ValueError
        row = Attempt.objects.get(
            pk=UUID(marker["attempt"]),
            connection_id=UUID(marker["connection"]),
            connection__workspace_id=binding[1],
        )
        candidate._metadata(row)
        if (
            str(row.generation) != marker["generation"]
            or row.expected_revision != marker["revision"]
        ):
            raise ValueError
        candidate.consume_candidate(
            owner=request.user,
            workspace_id=binding[1],
            connection_id=row.connection_id,
            attempt_id=row.pk,
            session_key=binding[2],
            query=query,
        )
        request.session["scoped_candidate_notice"] = "callback_result"
    except Exception:
        # Sanitized marker only. No callback query/code/state/verifier in session.
        request.session["scoped_candidate_notice"] = "callback_denied"
    return HttpResponseRedirect(STATUS_PATH, status=303)


@_guard("POST")
@csrf_protect
@sensitive_variables()
def retire(request, binding):
    try:
        value = _submitted(request, binding, "retire")
        row = Attempt.objects.get(
            pk=UUID(value["attempt"]),
            connection_id=UUID(value["connection"]),
            connection__workspace_id=binding[1],
        )
        candidate._metadata(row)
        retire_reserved(
            owner=request.user,
            workspace_id=binding[1],
            connection_id=row.connection_id,
            attempt_id=row.pk,
            request_id=UUID(value["operation"]),
            expected_generation=UUID(value["generation"]),
            expected_revision=value["revision"],
            retirement_confirmation=True,
            expected_receipt_key=value["receipt"],
        )
        marker = request.session.get(MARKER)
        if isinstance(marker, dict) and marker.get("attempt") == str(row.pk):
            request.session.pop(MARKER, None)
        request.session["scoped_candidate_notice"] = "retired"
        return HttpResponseRedirect(STATUS_PATH, status=303)
    except (
        signing.BadSignature,
        ValueError,
        TypeError,
        IdentityConflict,
        Attempt.DoesNotExist,
    ):
        return _problem(request)
