"""Local Google authorization endpoints."""

from django.urls import path

from . import draft_review, views

urlpatterns = [
    path(
        "total-budget-validate/",
        draft_review.validate_total_budget,
        name="google-local-total-budget-validate",
    ),
    path(
        "draft-status/", draft_review.dispatch_status, name="google-local-draft-status"
    ),
    path("draft-dispatch/", draft_review.dispatch, name="google-local-draft-dispatch"),
    path("draft-review/", draft_review.review, name="google-local-draft-review"),
    path("draft-approve/", draft_review.approve, name="google-local-draft-approve"),
    path("", views.status, name="google-local-status"),
    path("start/", views.start, name="google-local-start"),
    path("callback/", views.callback, name="google-local-callback"),
    path("disconnect/", views.disconnect, name="google-local-disconnect"),
    path("verify/", views.verify_test_account, name="google-local-verify"),
    path(
        "test-campaign/", views.test_campaign_action, name="google-local-test-campaign"
    ),
]
