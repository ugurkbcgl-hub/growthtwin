"""Authenticated synthetic start/read journey. No provider or credential access."""

from functools import wraps

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST, require_safe

from growthtwin.modules.workspaces.models import Workspace

from .lifecycle_codec import InvalidClosureState
from .lifecycle_decision import RequestFacts, evaluate_closure
from .lifecycle_journey import example_id, start_example
from .lifecycle_store import ClosureConflict, get_synthetic_closure
from .models import SyntheticClosureRequest


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
        request_id = example_id(workspace.pk, "request")
        exists = SyntheticClosureRequest.objects.filter(
            workspace=workspace, pk=request_id
        ).exists()
        rows.append(
            {"workspace": workspace, "request_id": request_id if exists else None}
        )
    return render(request, "connections/closure_overview.html", {"rows": rows})


@never_cache
@_enabled
@login_required
@require_POST
def start(request, workspace_id):
    _owner_workspace(request, workspace_id)
    allowed = {"csrfmiddlewaretoken", "synthetic_only"}
    if (
        set(request.POST) - allowed
        or request.FILES
        or request.POST.getlist("synthetic_only") != ["yes"]
        or any(len(request.POST.getlist(key)) != 1 for key in request.POST)
    ):
        return _problem(request, 400)
    try:
        record = start_example(owner=request.user, workspace_id=workspace_id)
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
    return render(
        request,
        "connections/closure_status.html",
        {
            "workspace": workspace,
            "messages": decision.messages,
            "has_pending": record.pending is not None
            or record.priority_pending is not None,
        },
    )
