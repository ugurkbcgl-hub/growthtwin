"""Whitelisted values for the synthetic-only campaign workspace prototype."""

SYNTHETIC_BUDGET_CHOICES = (
    ("250000", "2.500,00 TRY"),
    ("500000", "5.000,00 TRY"),
    ("1000000", "10.000,00 TRY"),
)
SYNTHETIC_DURATION_CHOICES = (("7", "7 gün"), ("14", "14 gün"), ("30", "30 gün"))

ALLOWED_SYNTHETIC_BUDGETS_MINOR = frozenset(
    int(value) for value, _label in SYNTHETIC_BUDGET_CHOICES
)
ALLOWED_SYNTHETIC_DURATIONS_DAYS = frozenset(
    int(value) for value, _label in SYNTHETIC_DURATION_CHOICES
)
