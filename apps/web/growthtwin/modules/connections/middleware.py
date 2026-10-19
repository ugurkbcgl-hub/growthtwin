"""Keep all connection responses private, including framework-level errors."""


class LocalOAuthHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/connections/google"):
            response["Cache-Control"] = "no-store, private"
            # no-referrer on the form document can make POST Origin opaque
            # (null), which Django correctly rejects. Same-origin permits the
            # local CSRF check without sharing referrers with Google.
            response["Referrer-Policy"] = (
                "same-origin"
                if request.path == "/connections/google/"
                else "no-referrer"
            )
        return response
