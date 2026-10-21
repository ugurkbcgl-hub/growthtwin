"""Authenticated synthetic start/read journey. No provider or credential access."""

from functools import wraps
from uuid import UUID

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST, require_safe

from growthtwin.modules.workspaces.models import Workspace

from .lifecycle_codec import InvalidClosureState
from .lifecycle_decision import RequestFacts, evaluate_closure
from .lifecycle_journey import EXAMPLES, example_id, start_example
from .lifecycle_results import complete_example, example_for_record, result_available
from .lifecycle_store import ClosureConflict, get_synthetic_closure
from .models import SyntheticClosureRequest

RESULT_SALT = "growthtwin.synthetic-closure-result.v1"


def _enabled(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not settings.SYNTHETIC_CLOSURE_UI_ENABLED:
            raise Http404("Sayfa bulunamadı.")
        return view(request, *args, **kwargs)

    return wrapped


def _owner_workspace(request, workspace_id):
    if not request.user.is_active:
        raise PermissionDenied
    return get_object_or_404(
        Workspace, pk=workspace_id, owner=request.user, owner__is_active=True
    )


def _problem(request, status_code):
    # Never reflect payload, DB metadata, IDs or exception strings in errors.
    return render(request, "connections/closure_problem.html", status=status_code)


@never_cache
@_enabled
@login_required
@require_safe
def overview(request):
    if not request.user.is_active:
        raise PermissionDenied
    rows = []
    for workspace in Workspace.objects.filter(
        owner=request.user, owner__is_active=True
    ):
        for example, label in EXAMPLES:
            request_id = example_id(workspace.pk, "request", example)
            exists = SyntheticClosureRequest.objects.filter(
                workspace=workspace, pk=request_id
            ).exists()
            rows.append(
                {
                    "workspace": workspace,
                    "example": example,
                    "label": label,
                    "request_id": request_id if exists else None,
                }
            )
    return render(request, "connections/closure_overview.html", {"rows": rows})


@never_cache
@_enabled
@login_required
@require_POST
def start(request, workspace_id, example="durdurma"):
    _owner_workspace(request, workspace_id)
    if example not in dict(EXAMPLES):
        raise Http404("Örnek bulunamadı.")
    allowed = {"csrfmiddlewaretoken", "synthetic_only"}
    if (
        set(request.POST) - allowed
        or request.FILES
        or request.POST.getlist("synthetic_only") != ["yes"]
        or any(len(request.POST.getlist(key)) != 1 for key in request.POST)
    ):
        return _problem(request, 400)
    try:
        record = start_example(
            owner=request.user, workspace_id=workspace_id, example=example
        )
    except (ClosureConflict, InvalidClosureState):
        return _problem(request, 409)
    except Workspace.DoesNotExist:
        raise Http404("Çalışma alanı bulunamadı.") from None
    return redirect(
        "closure:status",
        workspace_id=workspace_id,
        request_id=record.identity.request_id,
    )


@never_cache
@_enabled
@login_required
@require_safe
def status(request, workspace_id, request_id):
    workspace = _owner_workspace(request, workspace_id)
    try:
        record = get_synthetic_closure(
            owner=request.user, workspace_id=workspace_id, request_id=request_id
        )
    except (Workspace.DoesNotExist, SyntheticClosureRequest.DoesNotExist):
        raise Http404("Örnek bulunamadı.") from None
    except InvalidClosureState:
        return _problem(request, 409)
    decision = evaluate_closure(RequestFacts(True, True, True, True), record.snapshot)
    token = None
    if result_available(workspace_id, record):
        token = signing.dumps(
            {
                "owner": request.user.pk,
                "workspace": workspace_id,
                "request": str(request_id),
                "operation": str(record.pending.operation_id),
                "revision": record.revision,
            },
            salt=RESULT_SALT,
        )
    return render(
        request,
        "connections/closure_status.html",
        {
            "workspace": workspace,
            "messages": decision.messages,
            "has_pending": record.pending is not None
            or record.priority_pending is not None,
            "result_token": token,
            "example_label": dict(EXAMPLES).get(
                example_for_record(workspace_id, record)
            ),
            "request_id": request_id,
        },
    )


@never_cache
@_enabled
@login_required
@require_POST
def result(request, workspace_id, request_id):
    _owner_workspace(request, workspace_id)
    allowed = {"csrfmiddlewaretoken", "synthetic_only", "token"}
    if (
        set(request.POST) - allowed
        or request.FILES
        or request.POST.getlist("synthetic_only") != ["yes"]
        or len(request.POST.getlist("token")) != 1
        or any(len(request.POST.getlist(key)) != 1 for key in request.POST)
    ):
        return _problem(request, 400)
    try:
        payload = signing.loads(request.POST["token"], salt=RESULT_SALT, max_age=600)
        if (
            type(payload) is not dict
            or set(payload)
            != {"owner", "workspace", "request", "operation", "revision"}
            or payload["owner"] != request.user.pk
            or payload["workspace"] != workspace_id
            or payload["request"] != str(request_id)
        ):
            return _problem(request, 409)
        # UUID conversion is only for the already signed scoped operation ID.
        complete_example(
            owner=request.user,
            workspace_id=workspace_id,
            request_id=request_id,
            operation_id=UUID(payload["operation"]),
            expected_revision=payload["revision"],
        )
    except (
        signing.BadSignature,
        ClosureConflict,
        InvalidClosureState,
        ValueError,
        TypeError,
    ):
        return _problem(request, 409)
    except (Workspace.DoesNotExist, SyntheticClosureRequest.DoesNotExist):
        raise Http404("Örnek bulunamadı.") from None
    return redirect("closure:status", workspace_id=workspace_id, request_id=request_id)
