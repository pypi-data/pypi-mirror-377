import os
import warnings
from typing import Any

import sys

from smart_covdefaults.version_util import Version


class BadConditionWarning(Warning):
    """Raised when condition failed to evaluate."""


def _warn_eval_failed(expr: str, exception: Exception):
    warnings.warn(
        message=(
            f"Condition failed to evaluate:\n"
            f">>> {expr}\n"
            f"{exception}"
        ),
        category=BadConditionWarning
    )


def _gen_env() -> dict[str, Any]:
    return {
        "os": os,
        "sys": sys,
        "py": Version(sys.version_info[0], sys.version_info[1])
    }


def _eval_condition(condition: str) -> bool:
    try:
        return eval(condition, _gen_env())
    except Exception as exc:
        _warn_eval_failed(condition, exc)
        return False


def _select_enabled(patterns_conditions: dict[str, str]) -> list[str]:
    return [
        pattern
        for pattern, condition in patterns_conditions.items()
        if _eval_condition(condition)
    ]


def _parse_condition_dict(condition_list: list[str]) -> dict[str, str]:
    patterns_conditions = {}
    state = "pattern"
    pattern = None
    for item in condition_list:
        if not item:
            continue
        if state == "pattern":
            pattern = item
            state = "condition"
        elif state == "condition":
            patterns_conditions[pattern] = item
            state = "pattern"
    return patterns_conditions


def exclude_for_conditions(condition_option: list[str]) -> list[str]:
    return _select_enabled(_parse_condition_dict(condition_option))
