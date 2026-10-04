"""Generate one fixed synthetic image through a ZDR-pinned OpenRouter route."""

import argparse
import base64
import binascii
import json
import os
import sys
from datetime import datetime, timezone
from http.client import HTTPSConnection
from pathlib import Path
from uuid import uuid4

from growthtwin.modules.ai_gateway.evaluation_budget import (
    get_evaluation_budget_state,
    reserve_evaluation_cost,
    settle_evaluation_cost,
)

MODEL = "google/gemini-3.1-flash-lite-image"
PROVIDER = "google-vertex/global"
RESERVATION_USD = 0.10
LIST_IMAGE_COST_USD = 0.0336
MAX_PROMPT_BYTES = 4_096
MAX_RESPONSE_BYTES = 24_000_000
MAX_IMAGE_BYTES = 16_000_000
TIMEOUT_SECONDS = 180
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SYNTHETIC_PROMPT = (
    "Create one polished vertical advertising photograph for a fictional "
    "Turkish coffee roaster. Show a plain, unbranded 250 g terracotta coffee "
    "bag and a ceramic cup on a bright kitchen table, with subtle coastal "
    "Izmir morning light and tasteful editorial food photography. Leave the "
    "upper third uncluttered for later deterministic copy placement. No text, "
    "letters, labels, logos, trademarks, people, discount or health claims, "
    "phone numbers, guarantees, badges, or platform interface. Depict only "
    "the product and setting described. Synthetic evaluation artwork only."
)


def _local_directory() -> Path:
    local_data = os.environ.get("LOCALAPPDATA")
    local_root = Path(local_data) if local_data else Path.home() / "AppData/Local"
    result_directory = local_root / "GrowthTwin" / "evaluations" / "visual"
    repository_root = Path(__file__).resolve().parents[2]
    result_directory.mkdir(parents=True, exist_ok=True)
    resolved_directory = result_directory.resolve()
    if resolved_directory.is_relative_to(repository_root):
        raise OSError("Evaluation results must be stored outside the repository.")
    return resolved_directory


def _append_jsonl(path: Path, record: dict[str, object]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as capture:
        capture.write(json.dumps(record, separators=(",", ":")) + "\n")
        capture.flush()
        os.fsync(capture.fileno())


def _request_body() -> bytes:
    payload = {
        "model": MODEL,
        "prompt": SYNTHETIC_PROMPT,
        "n": 1,
        "resolution": "1K",
        "aspect_ratio": "9:16",
        "provider": {"only": [PROVIDER], "allow_fallbacks": False},
    }
    body = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode()
    if len(body) > MAX_PROMPT_BYTES:
        raise ValueError("Fixed synthetic image request exceeds its size limit.")
    return body


def _generate(api_key: str) -> tuple[bytes, float]:
    connection = HTTPSConnection("openrouter.ai", timeout=TIMEOUT_SECONDS)
    try:
        connection.request(
            "POST",
            "/api/v1/images",
            body=_request_body(),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        response = connection.getresponse()
        response_body = response.read(MAX_RESPONSE_BYTES + 1)
        if len(response_body) > MAX_RESPONSE_BYTES:
            raise ValueError("Image provider response exceeded the size limit.")
        if response.status != 200:
            raise RuntimeError("Image provider request failed; no retry was made.")
    finally:
        connection.close()

    try:
        result = json.loads(response_body)
        data = result["data"]
        cost = result["usage"]["cost"]
        encoded = data[0]["b64_json"]
    except (
        KeyError,
        IndexError,
        TypeError,
        json.JSONDecodeError,
    ) as error:
        raise ValueError(
            "Image response or provider cost was not verifiable."
        ) from error

    if (
        not isinstance(data, list)
        or len(data) != 1
        or type(cost) not in (int, float)
        or not 0 <= cost <= RESERVATION_USD
        or not isinstance(encoded, str)
        or len(encoded) > MAX_IMAGE_BYTES * 2
    ):
        raise ValueError("Image count, cost, or encoded output exceeded its bound.")
    try:
        image_bytes = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as error:
        raise ValueError("Image output was not valid base64.") from error
    if len(image_bytes) > MAX_IMAGE_BYTES or not image_bytes.startswith(PNG_SIGNATURE):
        raise ValueError("Image output was not a bounded PNG file.")
    return image_bytes, float(cost)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--estimate",
        action="store_true",
        help="Show the fixed request and reservation without network access.",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run the single pre-authorized synthetic image request.",
    )
    args = parser.parse_args()
    if args.estimate == args.run:
        parser.error("Choose exactly one of --estimate or --run.")

    if args.estimate:
        print(
            f"One {MODEL} 1K 9:16 image; list image price USD "
            f"{LIST_IMAGE_COST_USD:.4f}; local maximum reservation USD "
            f"{RESERVATION_USD:.2f}. Estimate only; no key or network used."
        )
        return 0

    if os.environ.get("GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED") != "1":
        print(
            "The verified no-reset API-key cap was not asserted by the local launcher.",
            file=sys.stderr,
        )
        return 2
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if (
        not isinstance(api_key, str)
        or not api_key.strip()
        or len(api_key) > 512
        or "\r" in api_key
        or "\n" in api_key
    ):
        print("The protected OpenRouter credential is unavailable.", file=sys.stderr)
        return 2

    run_id = uuid4().hex
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    try:
        output_directory = _local_directory()
        capture_path = output_directory / f"image-{timestamp}-{run_id[:8]}.jsonl"
        with capture_path.open("x", encoding="utf-8", newline="\n") as capture:
            capture.write(
                json.dumps(
                    {
                        "record_type": "run",
                        "run_id": run_id,
                        "started_at_utc": datetime.now(timezone.utc).isoformat(),
                        "provider": "openrouter",
                        "model": MODEL,
                        "provider_endpoint": PROVIDER,
                        "synthetic_only": True,
                        "publishable": False,
                    },
                    separators=(",", ":"),
                )
                + "\n"
            )
            capture.flush()
            os.fsync(capture.fileno())
    except OSError as error:
        print(f"Could not prepare local-only output storage: {error}", file=sys.stderr)
        return 2

    try:
        ledger_path = reserve_evaluation_cost(
            RESERVATION_USD, per_request_limit_usd=RESERVATION_USD
        )
    except (OSError, RuntimeError, ValueError) as error:
        print(
            f"Image request stopped by the local budget ledger: {error}",
            file=sys.stderr,
        )
        return 2

    print("Sending one synthetic image request; no retries or alternate providers.")
    try:
        image_bytes, actual_cost = _generate(api_key)
    except Exception:
        print(
            "Image request did not produce verifiable output; its local "
            "reservation remains held. Sensitive details were suppressed.",
            file=sys.stderr,
        )
        return 1

    try:
        settle_evaluation_cost(ledger_path, RESERVATION_USD, actual_cost)
        image_path = output_directory / f"image-{timestamp}-{run_id[:8]}.png"
        with image_path.open("xb") as image_file:
            image_file.write(image_bytes)
            image_file.flush()
            os.fsync(image_file.fileno())
        _append_jsonl(
            capture_path,
            {
                "record_type": "completed",
                "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                "usage_cost_usd": actual_cost,
                "local_image_path": str(image_path),
                "publishable": False,
            },
        )
    except Exception:
        print(
            "Image generation returned, but local accounting or storage failed. "
            "Do not retry; inspect the local ledger before any further call.",
            file=sys.stderr,
        )
        return 1

    try:
        _, spent, reserved = get_evaluation_budget_state()
        print(
            f"Saved one review-only synthetic PNG locally. Provider-reported "
            f"cost: USD {actual_cost:.6f}. Local evaluation ledger: spent "
            f"USD {spent:.6f}; reserved USD {reserved:.6f}."
        )
        print(str(image_path))
    except Exception:
        print(
            "Image saved and reservation settled; local ledger summary could "
            "not be read.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
