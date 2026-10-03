"""Run the fixed synthetic creative suite against one bounded OpenAI model."""

import argparse
import json
import sys

from evaluate_local_ollama import CASES

from growthtwin.modules.ai_gateway.benchmark import run_text_benchmark
from growthtwin.modules.ai_gateway.evaluation_budget import (
    get_evaluation_budget_state,
    reserve_evaluation_cost,
    settle_evaluation_cost,
)
from growthtwin.modules.ai_gateway.openai import (
    MAX_OUTPUT_TOKENS,
    OPENAI_MODEL,
    OpenAICreativeGenerator,
)
from growthtwin.modules.ai_gateway.profiles import CREATIVE_COPY_PROFILE

REPETITIONS = 3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--estimate",
        action="store_true",
        help="Print the upper reservation for one fixed run; make no network calls.",
    )
    args = parser.parse_args()
    try:
        generator = OpenAICreativeGenerator(
            api_key="estimate-only" if args.estimate else None
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
            f"One fixed {OPENAI_MODEL} synthetic run: 9 calls, "
            f"at most ${total_reservation:.6f} reserved by the local ledger. "
            "Estimate only; no API request or spend occurred."
        )
        return 0

    print(
        "Synthetic-only OpenAI evaluation: one model, three fixed briefs, "
        "three repetitions per brief; no retries, tools, storage, or route use."
    )
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

            record = run_text_benchmark(
                CREATIVE_COPY_PROFILE,
                (case,),
                ((generator.generator_id, generator),),
                repetitions=1,
            )[0]
            if generator.last_usage is None or generator.last_cost_usd is None:
                print(
                    json.dumps(
                        {
                            **record.as_record(),
                            "repetitions_requested": REPETITIONS,
                            "repetition": repetition,
                            "provider": "openai",
                            "model": OPENAI_MODEL,
                            "response_model": generator.last_model,
                            "usage": None,
                            "estimated_cost_usd": None,
                            "budget_reservation_held": True,
                            "publishable": False,
                        },
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
                settle_evaluation_cost(
                    ledger_path,
                    reservation,
                    generator.last_cost_usd,
                )
            except (OSError, RuntimeError, ValueError) as error:
                print(
                    f"Evaluation stopped on budget accounting: {error}",
                    file=sys.stderr,
                )
                return 5

            print(
                json.dumps(
                    {
                        **record.as_record(),
                        "repetitions_requested": REPETITIONS,
                        "repetition": repetition,
                        "provider": "openai",
                        "model": OPENAI_MODEL,
                        "response_model": generator.last_model,
                        "usage": generator.last_usage,
                        "estimated_cost_usd": generator.last_cost_usd,
                        "budget_reservation_held": False,
                        "publishable": False,
                    },
                    ensure_ascii=True,
                ),
                flush=True,
            )
            completed += 1

    print(
        f"Completed {completed} synthetic calls against {OPENAI_MODEL}. "
        "Manually review claims, usefulness, diversity, and correction effort."
    )
    try:
        cap, spent, reserved = get_evaluation_budget_state()
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Could not read evaluation budget ledger: {error}", file=sys.stderr)
        return 6
    print(
        "Budget ledger: "
        f"${spent:.6f} estimated spent, ${reserved:.6f} reserved, "
        f"${max(0.0, cap - spent - reserved):.6f} available "
        f"of ${cap:.2f} local allocation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
