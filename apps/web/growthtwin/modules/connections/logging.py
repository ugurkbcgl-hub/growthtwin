"""Defense in depth for future callback requests in Django log handlers."""

import logging
from urllib.parse import unquote

from .google_oauth import CALLBACK_PATH


class OAuthCallbackFilter(logging.Filter):
    def filter(self, record):
        try:
            message = unquote(record.getMessage())
            request_path = unquote(
                getattr(getattr(record, "request", None), "path", "")
            )
        except Exception:
            return False
        # Drop the whole record, including exception data and request extras.
        # This is not a proxy/router log protection or a generic secret filter.
        path_prefix = CALLBACK_PATH.rstrip("/")
        return path_prefix not in message and path_prefix not in request_path
