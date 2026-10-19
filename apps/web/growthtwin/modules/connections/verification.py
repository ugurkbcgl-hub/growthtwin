"""One fixed read against an explicitly configured Google Ads test child."""

import hashlib
import json
import re
from urllib.request import Request, build_opener

from django.conf import settings
from django.views.decorators.debug import sensitive_variables

from . import backend
from .google_oauth import ADS_SCOPE

QUERY = (
    "SELECT customer.id, customer.test_account, customer.manager FROM customer LIMIT 1"
)


def _targets():
    customer = getattr(settings, "GOOGLE_ADS_LOCAL_TEST_CUSTOMER_ID", "")
    manager = getattr(settings, "GOOGLE_ADS_LOCAL_TEST_MANAGER_ID", "")
    if (
        not isinstance(customer, str)
        or not isinstance(manager, str)
        or not re.fullmatch(r"[0-9]{10}", customer)
        or not re.fullmatch(r"[0-9]{10}", manager)
        or customer == manager
    ):
        raise backend.ConnectionUnavailable("Explicit test targets are required.")
    return customer, manager


def configuration_key(binding):
    backend._enabled()
    customer, manager = _targets()
    try:
        encrypted = backend._token_path(binding).read_bytes()
        return hashlib.sha256(
            json.dumps([binding[:2], customer, manager]).encode() + encrypted
        ).hexdigest()
    except Exception:
        raise backend.ConnectionUnavailable(
            "Saved authorization is unavailable."
        ) from None


@sensitive_variables()
def verify(binding):
    backend._enabled()
    customer, manager = _targets()
    with backend._LOCK:
        key = configuration_key(binding)
        saved = backend._read(backend._token_path(binding))
        client = backend._client()
        try:
            if saved.get("scope") != ADS_SCOPE:
                raise ValueError
            token = json.loads(
                backend._post(
                    "https://oauth2.googleapis.com/token",
                    {
                        "client_id": client["client_id"],
                        "client_secret": client["client_secret"],
                        "refresh_token": saved["refresh_token"],
                        "grant_type": "refresh_token",
                    },
                )
            )
            if (
                not isinstance(token.get("access_token"), str)
                or not token["access_token"]
                or token.get("token_type", "").lower() != "bearer"
            ):
                raise ValueError
            request = Request(
                f"https://googleads.googleapis.com/v25/customers/{customer}/googleAds:search",
                data=json.dumps({"query": QUERY}).encode(),
                headers={
                    "Authorization": "Bearer " + token["access_token"],
                    "login-customer-id": manager,
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with build_opener(backend._NoRedirect()).open(
                request, timeout=25
            ) as response:
                body = response.read(65537)
                if response.status != 200 or len(body) > 65536:
                    raise ValueError
                payload = json.loads(body)
            rows = payload.get("results", [])
            if (
                payload.get("nextPageToken")
                or len(rows) != 1
                or str(rows[0].get("customer", {}).get("id")) != customer
                or rows[0]["customer"].get("testAccount") is not True
                or rows[0]["customer"].get("manager", False) is not False
                or key != configuration_key(binding)
            ):
                raise ValueError
            return key
        except Exception:
            raise backend.ConnectionUnavailable(
                "The configured test account could not be verified."
            ) from None
