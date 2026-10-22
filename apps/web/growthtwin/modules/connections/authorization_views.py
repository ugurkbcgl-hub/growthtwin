"""Owner/session/CSRF rehearsal: fixed fake only, never the OAuth adapter."""

from functools import wraps
from uuid import UUID, uuid4

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST, require_safe

from growthtwin.modules.workspaces.models import Workspace

from . import synthetic_authorization as rehearsal
from .connector_identity import IdentityConflict, get_identity
from .models import ConnectorIdentity, SyntheticAuthorizationAttempt

SALT = "growthtwin.synthetic-authorization-form.v1"
MARKER = "synthetic_connector_attempt"
LABELS = {
    "pending": "Örnek başlatıldı; sonuç henüz çalıştırılmadı.",
    "running": "Örnek sonuç belirsiz; otomatik tekrar yapılmaz.",
    "accepted": "Başarı örneği kaydedildi. Gerçek hesap bağlanmadı.",
    "rejected": "Örnek kabul edilmedi. Gerçek hesap bağlanmadı.",
    "expired": "Örneğin süresi doldu. Yeni bir prova başlatabilirsin.",
}


def _enabled(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if (
            settings.SYNTHETIC_CONNECTOR_UI_ENABLED is not True
            or settings.SYNTHETIC_CONNECTOR_AUTHORIZATION_ENABLED is not True
        ):
            raise Http404
        return view(request, *args, **kwargs)

    return wrapped


def _workspace(request, workspace_id):
    if not request.user.is_active:
        raise PermissionDenied
    return get_object_or_404(
        Workspace, pk=workspace_id, owner=request.user, owner__is_active=True
    )


def _session(request):
    if not request.session.session_key:
        raise PermissionDenied
    return salted_hmac(
        SALT, request.session.session_key, algorithm="sha256"
    ).hexdigest()


def _payload(request, workspace_id, snapshot, *, attempt_id, scenario):
    return {
        "owner": request.user.pk,
        "workspace": workspace_id,
        "session": _session(request),
        "connection": str(snapshot.connection_id),
        "generation": str(snapshot.generation),
        "revision": snapshot.revision,
        "attempt": str(attempt_id),
        "scenario": str(scenario),
    }


def _problem(request, code=409):
    return render(
        request,
        "connections/authorization_rehearsal.html",
        {
            "problem": True,
            "retry_url": reverse(
                "authorization_rehearsal:overview",
                args=[request.resolver_match.kwargs["workspace_id"]],
            ),
        },
        status=code,
    )


def _submitted(request, workspace_id, action):
    allowed = {"csrfmiddlewaretoken", "token", "synthetic_only"}
    if (
        set(request.POST) - allowed
        or request.FILES
        or request.POST.getlist("synthetic_only") != ["yes"]
        or len(request.POST.getlist("token")) != 1
        or len(request.POST["token"]) > 4096
        or any(len(request.POST.getlist(key)) != 1 for key in request.POST)
    ):
        raise ValueError
    value = signing.loads(request.POST["token"], salt=SALT, max_age=600)
    if (
        type(value) is not dict
        or set(value)
        != (
            {
                "owner",
                "workspace",
                "session",
                "connection",
                "generation",
                "revision",
                "attempt",
                "scenario",
                "action",
            }
            | ({"receipt_expires"} if action == "recover" else set())
        )
        or value["owner"] != request.user.pk
        or value["workspace"] != workspace_id
        or value["session"] != _session(request)
        or value["action"] != action
        or type(value["revision"]) is not int
        or type(value["owner"]) is not int
        or type(value["workspace"]) is not int
        or any(
            type(value[key]) is not str
            for key in (
                "session",
                "connection",
                "generation",
                "attempt",
                "scenario",
                "action",
            )
        )
    ):
        raise ValueError
    for key in ("connection", "generation", "attempt"):
        parsed = UUID(value[key])
        if not parsed.int or str(parsed) != value[key]:
            raise ValueError
    if action == "recover" and type(value["receipt_expires"]) is not str:
        raise ValueError
    return {key: item for key, item in value.items() if key != "action"}


@never_cache
@_enabled
@login_required
@require_safe
def overview(request, workspace_id):
    workspace = _workspace(request, workspace_id)
    connector = ConnectorIdentity.objects.filter(
        workspace=workspace, provider="google_ads_test"
    ).first()
    examples = []
    if connector:
        try:
            snapshot = get_identity(
                owner=request.user,
                workspace_id=workspace_id,
                connection_id=connector.pk,
            )
            if snapshot.state == ConnectorIdentity.State.QUARANTINED:
                for scenario, label in (
                    (rehearsal.FakeAuthorizationScenario.ALLOW, "Başarı örneği"),
                    (rehearsal.FakeAuthorizationScenario.DENY, "Ret örneği"),
                ):
                    value = _payload(
                        request,
                        workspace_id,
                        snapshot,
                        attempt_id=uuid4(),
                        scenario=scenario,
                    )
                    examples.append(
                        {
                            "label": label,
                            "token": signing.dumps(
                                value | {"action": "start"}, salt=SALT
                            ),
                        }
                    )
        except IdentityConflict:
            return _problem(request)
    return render(
        request,
        "connections/authorization_rehearsal.html",
        {"workspace": workspace, "examples": examples},
    )


@never_cache
@_enabled
@login_required
@require_POST
def start(request, workspace_id):
    _workspace(request, workspace_id)
    try:
        value = _submitted(request, workspace_id, "start")
        snapshot = rehearsal.begin_example(
            owner=request.user,
            workspace_id=workspace_id,
            connection_id=UUID(value["connection"]),
            attempt_id=UUID(value["attempt"]),
            expected_generation=UUID(value["generation"]),
            expected_revision=value["revision"],
            scenario=rehearsal.FakeAuthorizationScenario(value["scenario"]),
            synthetic_confirmation=True,
        )
    except (signing.BadSignature, ValueError, TypeError, IdentityConflict):
        return _problem(request)
    except (Workspace.DoesNotExist, ConnectorIdentity.DoesNotExist):
        raise Http404 from None
    # Metadata only; login/session rotation invalidates prior forms and access.
    request.session[MARKER] = value
    return redirect(
        "authorization_rehearsal:status",
        workspace_id=workspace_id,
        connection_id=snapshot.connection_id,
        attempt_id=snapshot.attempt_id,
    )


def _lookup(request, workspace_id, connection_id, attempt_id):
    snapshot = rehearsal.get_example(
        owner=request.user,
        workspace_id=workspace_id,
        connection_id=connection_id,
        attempt_id=attempt_id,
    )
    current = get_identity(
        owner=request.user, workspace_id=workspace_id, connection_id=connection_id
    )
    value = _payload(
        request,
        workspace_id,
        current,
        attempt_id=attempt_id,
        scenario=snapshot.scenario,
    )
    # Preserve the original receipt generation/revision in the session binding.
    value["generation"], value["revision"] = (
        str(snapshot.generation),
        snapshot.expected_revision,
    )
    return snapshot, current, value


def _record(request, workspace_id, connection_id, attempt_id):
    snapshot, current, value = _lookup(request, workspace_id, connection_id, attempt_id)
    if request.session.get(MARKER) != value:
        raise Http404
    return snapshot, current, value


@never_cache
@_enabled
@login_required
@require_safe
def recovery(request, workspace_id):
    workspace = _workspace(request, workspace_id)
    rows = []
    # Fixed synthetic receipts ONLY. Never inspect candidate files or actual grants.
    records = SyntheticAuthorizationAttempt.objects.filter(
        connection__workspace=workspace
    ).order_by("-created_at")[:20]
    try:
        for record in records:
            snapshot, _, value = _lookup(
                request, workspace_id, record.connection_id, record.pk
            )
            ticket = signing.dumps(
                value
                | {
                    "action": "recover",
                    "receipt_expires": snapshot.expires_at.isoformat(),
                },
                salt=SALT,
            )
            rows.append(
                {
                    "snapshot": snapshot,
                    "message": LABELS[snapshot.state],
                    "token": ticket,
                    "scenario_label": "Başarı örneği"
                    if snapshot.scenario is rehearsal.FakeAuthorizationScenario.ALLOW
                    else "Ret örneği",
                }
            )
    except IdentityConflict:
        return _problem(request)
    except (
        Workspace.DoesNotExist,
        ConnectorIdentity.DoesNotExist,
        SyntheticAuthorizationAttempt.DoesNotExist,
    ):
        raise Http404 from None
    return render(
        request,
        "connections/authorization_recovery.html",
        {"workspace": workspace, "rows": rows},
    )


@never_cache
@_enabled
@login_required
@require_POST
def recover(request, workspace_id, connection_id, attempt_id):
    _workspace(request, workspace_id)
    try:
        value = _submitted(request, workspace_id, "recover")
        snapshot, _, expected = _lookup(
            request, workspace_id, connection_id, attempt_id
        )
        if value != expected | {"receipt_expires": snapshot.expires_at.isoformat()}:
            raise ValueError
    except (signing.BadSignature, ValueError, TypeError, IdentityConflict):
        return _problem(request)
    except (
        Workspace.DoesNotExist,
        ConnectorIdentity.DoesNotExist,
        SyntheticAuthorizationAttempt.DoesNotExist,
    ):
        raise Http404 from None
    # Deliberately rebind ONLY synthetic metadata. No reservation or fake execution.
    request.session[MARKER] = expected
    return redirect(
        "authorization_rehearsal:status",
        workspace_id=workspace_id,
        connection_id=connection_id,
        attempt_id=attempt_id,
    )


@never_cache
@_enabled
@login_required
@require_safe
def status(request, workspace_id, connection_id, attempt_id):
    workspace = _workspace(request, workspace_id)
    try:
        snapshot, current, value = _record(
            request, workspace_id, connection_id, attempt_id
        )
    except (
        Workspace.DoesNotExist,
        ConnectorIdentity.DoesNotExist,
        SyntheticAuthorizationAttempt.DoesNotExist,
    ):
        raise Http404 from None
    except IdentityConflict:
        return _problem(request)
    scope_matches = (
        current.state == "quarantined"
        and current.generation == snapshot.generation
        and current.revision == snapshot.expected_revision
    )
    expired = timezone.now() >= snapshot.expires_at
    can_perform = snapshot.state == "pending" and scope_matches and not expired
    token = (
        signing.dumps(value | {"action": "perform"}, salt=SALT) if can_perform else None
    )
    return render(
        request,
        "connections/authorization_rehearsal.html",
        {
            "workspace": workspace,
            "snapshot": snapshot,
            "message": LABELS[snapshot.state],
            "token": token,
            "scope_changed": not scope_matches,
            "expired": expired and snapshot.state == "pending",
        },
    )


@never_cache
@_enabled
@login_required
@require_POST
def perform(request, workspace_id, connection_id, attempt_id):
    _workspace(request, workspace_id)
    try:
        value = _submitted(request, workspace_id, "perform")
        snapshot, _, expected = _record(
            request, workspace_id, connection_id, attempt_id
        )
        if value != expected:
            raise ValueError
        rehearsal.perform_example(
            owner=request.user,
            workspace_id=workspace_id,
            connection_id=connection_id,
            attempt_id=snapshot.attempt_id,
        )
    except (signing.BadSignature, ValueError, TypeError, IdentityConflict):
        return _problem(request)
    except (
        Workspace.DoesNotExist,
        ConnectorIdentity.DoesNotExist,
        SyntheticAuthorizationAttempt.DoesNotExist,
    ):
        raise Http404 from None
    return redirect(
        "authorization_rehearsal:status",
        workspace_id=workspace_id,
        connection_id=connection_id,
        attempt_id=attempt_id,
    )
