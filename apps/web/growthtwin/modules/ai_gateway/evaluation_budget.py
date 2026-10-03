"""Small persistent spend ledger shared by explicitly invoked eval runners."""

import os
import sqlite3
from contextlib import closing
from pathlib import Path

# The owner confirmed USD 16 of existing OpenRouter credits on 2026-10-04.
# Do not replenish this balance automatically or add new credits.
APPROVED_EVALUATION_BUDGET_USD = 16.0


def _ledger_path() -> Path:
    root = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData/Local")
    return Path(root) / "GrowthTwin" / "ai-evaluation-budget.sqlite3"


def reserve_evaluation_cost(amount_usd: float) -> Path:
    """Atomically reserve a known upper bound before a billable call."""

    if type(amount_usd) not in (int, float) or not 0 < amount_usd <= 0.01:
        raise ValueError("Evaluation calls must have a positive small cost bound.")
    if os.environ.get("GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED") != "1":
        raise RuntimeError(
            "Set the provider project's hard spend limit before billable evaluation."
        )

    path = _ledger_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path, timeout=5)) as connection:
        with connection as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS budget ("
                "singleton INTEGER PRIMARY KEY CHECK (singleton = 1), "
                "cap_usd REAL NOT NULL, spent_usd REAL NOT NULL, "
                "reserved_usd REAL NOT NULL)"
            )
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT cap_usd, spent_usd, reserved_usd "
                "FROM budget WHERE singleton = 1"
            ).fetchone()
            if row is None:
                spent_usd = reserved_usd = 0.0
                db.execute(
                    "INSERT INTO budget VALUES (1, ?, 0, 0)",
                    (APPROVED_EVALUATION_BUDGET_USD,),
                )
            else:
                cap_usd, spent_usd, reserved_usd = row
                if cap_usd != APPROVED_EVALUATION_BUDGET_USD:
                    raise RuntimeError("Evaluation ledger cap does not match approval.")
            if spent_usd + reserved_usd + amount_usd > APPROVED_EVALUATION_BUDGET_USD:
                raise RuntimeError(
                    f"Approved ${APPROVED_EVALUATION_BUDGET_USD:.2f} "
                    "prepaid evaluation balance is exhausted."
                )
            db.execute(
                "UPDATE budget SET reserved_usd = reserved_usd + ? WHERE singleton = 1",
                (amount_usd,),
            )
    return path


def settle_evaluation_cost(path: Path, reserved_usd: float, actual_usd: float) -> None:
    """Replace a reservation with conservative token-based cost estimate."""

    if (
        not isinstance(path, Path)
        or type(reserved_usd) not in (int, float)
        or type(actual_usd) not in (int, float)
        or not 0 <= actual_usd <= reserved_usd
    ):
        raise ValueError("Provider-reported usage exceeded its safe reservation.")
    with closing(sqlite3.connect(path, timeout=5)) as connection:
        with connection as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT reserved_usd FROM budget WHERE singleton = 1"
            ).fetchone()
            if row is None or row[0] + 1e-12 < reserved_usd:
                raise RuntimeError("Evaluation reservation is missing or inconsistent.")
            db.execute(
                "UPDATE budget SET reserved_usd = reserved_usd - ?, "
                "spent_usd = spent_usd + ? WHERE singleton = 1",
                (reserved_usd, actual_usd),
            )


def get_evaluation_budget_state(path: Path | None = None) -> tuple[float, float, float]:
    """Return (cap, estimated spent, reserved) without exposing ledger contents."""

    ledger = path or _ledger_path()
    if not ledger.exists():
        return APPROVED_EVALUATION_BUDGET_USD, 0.0, 0.0
    with closing(sqlite3.connect(ledger, timeout=5)) as connection:
        row = connection.execute(
            "SELECT cap_usd, spent_usd, reserved_usd FROM budget WHERE singleton = 1"
        ).fetchone()
    if row is None or row[0] != APPROVED_EVALUATION_BUDGET_USD:
        raise RuntimeError("Evaluation budget ledger is missing or inconsistent.")
    return row
