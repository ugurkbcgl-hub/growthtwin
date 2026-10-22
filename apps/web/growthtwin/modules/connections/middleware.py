"""Keep all connection responses private, including framework-level errors."""


class LocalOAuthHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith(
            ("/workspace/control/", "/workspace/connection-rehearsal/")
        ) or (
            request.path.startswith("/workspace/campaigns/")
            and request.path.endswith("/journey/")
        ):
            response["Cache-Control"] = "no-store, private"
            response["Referrer-Policy"] = "same-origin"
            response["X-Robots-Tag"] = "noindex, nofollow"
        if request.path.startswith("/connections/google"):
            response["Cache-Control"] = "no-store, private"
            # no-referrer on the form document can make POST Origin opaque
            # (null), which Django correctly rejects. Same-origin permits the
            # local CSRF check without sharing referrers with Google.
            response["Referrer-Policy"] = (
                "same-origin"
                if request.path
                in {
                    "/connections/google/",
                    "/connections/google/draft-review/",
                    "/connections/google/draft-status/",
                    # Shared result/error pages include the same-origin logout
                    # form; retain CSRF Origin without sending external referrers.
                    "/connections/google/draft-dispatch/",
                    "/connections/google/draft-approve/",
                    "/connections/google/total-budget-validate/",
                }
                else "no-referrer"
            )
        return response
