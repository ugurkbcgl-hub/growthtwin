"""Run the fixed synthetic creative suite against OpenRouter GPT-6 Luna."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from evaluate_local_ollama import CASES

from growthtwin.modules.ai_gateway.benchmark import run_text_benchmark
from growthtwin.modules.ai_gateway.evaluation_budget import (
    get_evaluation_budget_state,
    reserve_evaluation_cost,
    settle_evaluation_cost,
)
from growthtwin.modules.ai_gateway.openrouter import (
    MAX_OUTPUT_TOKENS,
    MODEL_PRICE_CAPS,
    OPENROUTER_MODEL,
    OpenRouterCreativeGenerator,
)
from growthtwin.modules.ai_gateway.profiles import CREATIVE_COPY_PROFILE

REPETITIONS = 3


def _new_result_capture(model: str) -> tuple[Path, str]:
    """Create an exclusive JSONL file under local user data, outside Git."""

    local_data = os.environ.get("LOCALAPPDATA")
    local_root = Path(local_data) if local_data else Path.home() / "AppData/Local"
    result_directory = local_root / "GrowthTwin" / "evaluations"
    repository_root = Path(__file__).resolve().parents[2]
    result_directory.mkdir(parents=True, exist_ok=True)
    resolved_directory = result_directory.resolve()
    if resolved_directory.is_relative_to(repository_root):
        raise OSError("Evaluation results must be stored outside the repository.")

    run_id = uuid4().hex
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    result_path = resolved_directory / f"openrouter-{timestamp}-{run_id[:8]}.jsonl"
    with result_path.open("x", encoding="utf-8", newline="\n") as capture:
        capture.write(
            json.dumps(
                {
                    "record_type": "run",
                    "run_id": run_id,
                    "started_at_utc": datetime.now(timezone.utc).isoformat(),
                    "provider": "openrouter",
                    "model": model,
                    "profile_id": CREATIVE_COPY_PROFILE.profile_id,
                    "synthetic_only": True,
                    "publishable": False,
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
            + "\n"
        )
        capture.flush()
        os.fsync(capture.fileno())
    return result_path, run_id


def _append_result(result_path: Path, record: dict[str, object]) -> None:
    """Durably append one synthetic result or accounting event."""

    with result_path.open("a", encoding="utf-8", newline="\n") as capture:
        capture.write(
            json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
        )
        capture.flush()
        os.fsync(capture.fileno())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--estimate",
        action="store_true",
        help="Print the upper reservation for one fixed run; make no network calls.",
    )
    parser.add_argument(
        "--model",
        choices=tuple(MODEL_PRICE_CAPS),
        default=OPENROUTER_MODEL,
        help="Select one explicitly allowed synthetic evaluation candidate.",
    )
    args = parser.parse_args()
    try:
        generator = OpenRouterCreativeGenerator(
            api_key="estimate-only" if args.estimate else None, model=args.model
        )
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    if args.estimate:
        total_reservation = sum(
            generator.maximum_reserved_cost(generator.request_body(case.request))
            * REPETITIONS
            for case in CASES
        )
        print(
            f"One fixed {generator.model} synthetic run: 9 calls, "
            f"at most ${total_reservation:.6f} reserved by the local ledger. "
            "Estimate only; no API request or spend occurred."
        )
        return 0

    print(
        "Synthetic-only OpenRouter evaluation: one model, three fixed briefs, "
        "three repetitions per brief; no retries, tools, brief storage, or route use."
    )
    try:
        result_path, run_id = _new_result_capture(generator.model)
    except OSError as error:
        print(
            f"Could not prepare local result capture; no provider request was sent: {error}",
            file=sys.stderr,
        )
        return 7
    print(f"Synthetic results will be saved locally to: {result_path}")

    completed = 0
    for case in CASES:
        for repetition in range(1, REPETITIONS + 1):
            body = generator.request_body(case.request)
            reservation = generator.maximum_reserved_cost(body)
            try:
                ledger_path = reserve_evaluation_cost(reservation)
            except (OSError, RuntimeError, ValueError) as error:
                print(f"Evaluation stopped before request: {error}", file=sys.stderr)
                return 3

            call_id = f"{case.case_id}-{repetition}"
            try:
                _append_result(
                    result_path,
                    {
                        "record_type": "call_started",
                        "run_id": run_id,
                        "call_id": call_id,
                        "case_id": case.case_id,
                        "repetition": repetition,
                        "reserved_cost_usd": reservation,
                    },
                )
            except OSError as error:
                print(
                    "Local result capture failed before the provider request; "
                    f"the reservation remains held: {error}",
                    file=sys.stderr,
                )
                return 7

            record = run_text_benchmark(
                CREATIVE_COPY_PROFILE,
                (case,),
                ((generator.generator_id, generator),),
                repetitions=1,
            )[0]
            if generator.last_usage is None or generator.last_cost_usd is None:
                failed_record = {
                    **record.as_record(),
                    "record_type": "call_result",
                    "run_id": run_id,
                    "call_id": call_id,
                    "repetitions_requested": REPETITIONS,
                    "repetition": repetition,
                    "provider": "openrouter",
                    "model": generator.model,
                    "response_model": generator.last_model,
                    "upstream_provider": generator.last_provider,
                    "usage": None,
                    "estimated_cost_usd": None,
                    "budget_reservation_held": True,
                    "ledger_settlement": "not_verified",
                    "publishable": False,
                }
                try:
                    _append_result(result_path, failed_record)
                except OSError as error:
                    print(
                        "Local result capture failed after an unverified provider "
                        f"response; reservation remains held: {error}",
                        file=sys.stderr,
                    )
                    return 7
                print(
                    json.dumps(
                        failed_record,
                        ensure_ascii=True,
                    ),
                    flush=True,
                )
                print(
                    "Evaluation stopped after an unverified provider response; "
                    "its reservation remains charged in the local ledger.",
                    file=sys.stderr,
                )
                return 4
            try:
                if generator.last_usage["output_tokens"] > MAX_OUTPUT_TOKENS:
                    raise ValueError("Provider usage exceeded the fixed token cap.")
                successful_record = {
                    **record.as_record(),
                    "record_type": "call_result",
                    "run_id": run_id,
                    "call_id": call_id,
                    "repetitions_requested": REPETITIONS,
                    "repetition": repetition,
                    "provider": "openrouter",
                    "model": generator.model,
                    "response_model": generator.last_model,
                    "upstream_provider": generator.last_provider,
                    "usage": generator.last_usage,
                    "estimated_cost_usd": generator.last_cost_usd,
                    "budget_reservation_held": True,
                    "ledger_settlement": "pending",
                    "publishable": False,
                }
                _append_result(result_path, successful_record)
            except OSError as error:
                print(
                    "Local result capture failed after a provider response; "
                    f"the reservation remains held: {error}",
                    file=sys.stderr,
                )
                return 7

            try:
                settle_evaluation_cost(
                    ledger_path, reservation, generator.last_cost_usd
                )
            except (OSError, RuntimeError, ValueError) as error:
                print(
                    "Evaluation stopped on budget accounting; the saved result "
                    f"shows settlement pending: {error}",
                    file=sys.stderr,
                )
                return 5

            try:
                _append_result(
                    result_path,
                    {
                        "record_type": "ledger_settlement",
                        "run_id": run_id,
                        "call_id": call_id,
                        "status": "settled",
                        "provider_reported_cost_usd": generator.last_cost_usd,
                    },
                )
            except OSError as error:
                print(
                    "Local result capture failed after ledger settlement; "
                    f"stopping before another provider request: {error}",
                    file=sys.stderr,
                )
                return 7

            print(
                json.dumps(
                    {
                        **successful_record,
                        "budget_reservation_held": False,
                        "ledger_settlement": "settled",
                    },
                    ensure_ascii=True,
                ),
                flush=True,
            )
            completed += 1

    try:
        cap, spent, reserved = get_evaluation_budget_state()
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Could not read evaluation budget ledger: {error}", file=sys.stderr)
        return 6
    try:
        _append_result(
            result_path,
            {
                "record_type": "run_completed",
                "run_id": run_id,
                "calls_completed": completed,
                "budget_cap_usd": cap,
                "spent_usd": spent,
                "reserved_usd": reserved,
                "remaining_local_usd": max(0.0, cap - spent - reserved),
            },
        )
    except OSError as error:
        print(
            f"Local result capture failed while finalizing the run: {error}",
            file=sys.stderr,
        )
        return 7
    print(
        f"Completed {completed} synthetic calls against {generator.model}. "
        "Manually review claims, usefulness, diversity, and correction effort. "
        f"Result file: {result_path}"
    )
    print(
        "Budget ledger: "
        f"${spent:.6f} estimated spent, ${reserved:.6f} reserved, "
        f"${max(0.0, cap - spent - reserved):.6f} available "
        f"of ${cap:.2f} local allocation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
