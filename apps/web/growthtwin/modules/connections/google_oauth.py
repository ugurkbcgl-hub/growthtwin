"""Process-local OAuth preparation for an isolated local test server only.

No network, database, credential loading, or token persistence is performed here.
The caller must authorize the workspace and protect the start POST against CSRF.
"""

import base64
import hashlib
import secrets
import threading
import time
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlencode

CALLBACK_PATH = "/connections/google/callback/"
LOCAL_REDIRECT_URI = "http://127.0.0.1:8002" + CALLBACK_PATH
SCOPED_CALLBACK_PATH = "/connections/google/scoped/callback/"
SCOPED_REDIRECT_URI = "http://127.0.0.1:8002" + SCOPED_CALLBACK_PATH
ADS_SCOPE = "https://www.googleapis.com/auth/adwords"
AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"


class AuthorizationRejected(ValueError):
    """Deliberately excludes the callback and provider response from errors."""


@dataclass(frozen=True, repr=False)
class AuthorizationCode:
    code: str = field(repr=False)
    verifier: str = field(repr=False)


@dataclass(frozen=True, repr=False)
class _Pending:
    state: str
    verifier: str
    expires_at: float


class LocalAuthorizationStore:
    """Single-process, bounded, one active attempt per owner/workspace/session.

    Restarts discard outstanding attempts. Not suitable for multiple workers.
    Binding values must come from authenticated server state, never form fields.
    """

    def __init__(self, *, clock=time.monotonic):
        self._clock = clock
        self._pending = {}
        self._lock = threading.Lock()

    def begin(self, *, client_id, binding, redirect_uri=LOCAL_REDIRECT_URI):
        if (
            redirect_uri not in (LOCAL_REDIRECT_URI, SCOPED_REDIRECT_URI)
            or not isinstance(client_id, str)
            or not client_id.endswith(".apps.googleusercontent.com")
            or len(client_id) > 256
            or any(c.isspace() for c in client_id)
            or not isinstance(binding, tuple)
            or len(binding) != 3
            or not all(isinstance(value, str) and value for value in binding)
        ):
            raise AuthorizationRejected("Invalid local authorization configuration.")
        state = secrets.token_urlsafe(32)
        verifier = secrets.token_urlsafe(64)
        with self._lock:
            now = self._clock()
            self._pending = {
                key: value
                for key, value in self._pending.items()
                if value.expires_at > now
            }
            if binding not in self._pending and len(self._pending) >= 100:
                raise AuthorizationRejected("Authorization capacity reached.")
            self._pending[binding] = _Pending(state, verifier, now + 300)
        challenge = (
            base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest())
            .decode("ascii")
            .rstrip("=")
        )
        return (
            AUTHORIZATION_ENDPOINT
            + "?"
            + urlencode(
                {
                    "client_id": client_id,
                    "redirect_uri": redirect_uri,
                    "response_type": "code",
                    "scope": ADS_SCOPE,
                    "state": state,
                    "code_challenge": challenge,
                    "code_challenge_method": "S256",
                    "access_type": "offline",
                    "prompt": "consent",
                    "include_granted_scopes": "false",
                }
            )
        )

    def consume(self, *, binding, query):
        # Pop under a lock before validation: denial, malformed input and replay
        # all require a fresh start. Other owners' attempts remain untouched.
        with self._lock:
            pending = self._pending.pop(binding, None)
        if pending is None or pending.expires_at <= self._clock():
            raise AuthorizationRejected("Authorization expired or unavailable.")
        if not isinstance(query, str) or len(query) > 8192:
            raise AuthorizationRejected("Invalid authorization response.")
        try:
            values = parse_qs(query, keep_blank_values=True, max_num_fields=20)
        except ValueError:
            raise AuthorizationRejected("Invalid authorization response.") from None
        state = values.get("state", [])
        code = values.get("code", [])
        if (
            any(len(items) != 1 for items in values.values())
            or len(state) != 1
            or not state[0].isascii()
            or not secrets.compare_digest(state[0], pending.state)
            or "error" in values
            or len(code) != 1
            or not code[0]
            or len(code[0]) > 4096
            or not code[0].isascii()
            or any(ord(c) < 33 or ord(c) == 127 for c in code[0])
        ):
            raise AuthorizationRejected("Authorization was denied or invalid.")
        return AuthorizationCode(code[0], pending.verifier)
