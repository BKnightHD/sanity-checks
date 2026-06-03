# checks.py
# Each function receives the full dataframe and returns a result dict.
#
# Every check returns:
# {
#   "check":   str,        # name of the check
#   "status":  str,        # "pass", "fail", or "warn"
#   "message": str,        # human-readable summary
#   "details": list        # list of dicts with row-level detail (empty if pass)
# }

import pandas as pd
from schema import COLUMN_SCHEMA


# ---------------------------------------------------------------------------
# Helper: map our simple type names to a validation function
# ---------------------------------------------------------------------------

def _is_numeric(value) -> bool:
    if pd.isna(value):
        return True  # nulls are not a type violation — that's a separate check
    return isinstance(value, (int, float))


def _is_string(value) -> bool:
    if pd.isna(value):
        return True
    return isinstance(value, str)


def _is_date(value) -> bool:
    if pd.isna(value):
        return True
    return isinstance(value, (pd.Timestamp,))


def _is_boolean(value) -> bool:
    if pd.isna(value):
        return True
    return isinstance(value, bool)


TYPE_VALIDATORS = {
    "numeric": _is_numeric,
    "string":  _is_string,
    "date":    _is_date,
    "boolean": _is_boolean,
}


# ---------------------------------------------------------------------------
# Check 1: Column data types match the schema
# ---------------------------------------------------------------------------

def check_column_types(df: pd.DataFrame) -> dict:
    """
    For each column in COLUMN_SCHEMA, validates that every non-null value
    matches the expected type. Flags columns where violations are found
    and reports which rows are the problem.
    """
    check_name = "Column Type Validation"
    details = []
    missing_columns = []

    for col, expected_type in COLUMN_SCHEMA.items():

        # Check if the column even exists in the file
        if col not in df.columns:
            missing_columns.append(col)
            continue

        validator = TYPE_VALIDATORS[expected_type]

        # Find rows where the value fails the type check
        bad_rows = [
            {
                "row":      idx + 2,  # +2 because Excel rows start at 1 and row 1 is the header
                "column":   col,
                "value":    df.at[idx, col],
                "expected": expected_type,
            }
            for idx, value in enumerate(df[col])
            if not validator(value)
        ]

        if bad_rows:
            details.extend(bad_rows)

    # Build the result
    if missing_columns:
        return {
            "check":   check_name,
            "status":  "warn",
            "message": (
                f"{len(missing_columns)} column(s) in the schema were not found in the file: "
                f"{missing_columns}. Check for renamed or missing columns."
            ),
            "details": [],
        }

    if details:
        affected_columns = list({d["column"] for d in details})
        return {
            "check":   check_name,
            "status":  "fail",
            "message": (
                f"{len(details)} type violation(s) found across "
                f"{len(affected_columns)} column(s): {affected_columns}"
            ),
            "details": details,
        }

    return {
        "check":   check_name,
        "status":  "pass",
        "message": "All columns contain the expected data types.",
        "details": [],
    }