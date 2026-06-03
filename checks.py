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
# Helper: build a standard result dict
# ---------------------------------------------------------------------------

def _make_result(check_name: str, details: list, pass_message: str, fail_message_fn) -> dict:
    if details:
        return {
            "check":   check_name,
            "status":  "fail",
            "message": fail_message_fn(details),
            "details": details,
        }
    return {
        "check":   check_name,
        "status":  "pass",
        "message": pass_message,
        "details": [],
    }


# ---------------------------------------------------------------------------
# Helper: reusable size relationship checker (20' < 40' <= 40HC)
# ---------------------------------------------------------------------------

def _check_size_relationships(df: pd.DataFrame, col_20: str, col_40: str, col_40hc: str, check_name: str) -> dict:
    """
    Validates that values follow the expected container size pricing relationship:
      - 20' column < 40' column
      - 20' column < 40HC column
      - 40' column <= 40HC column
    Skips rows where any of the three values is null.
    """
    details = []

    missing = [c for c in [col_20, col_40, col_40hc] if c not in df.columns]
    if missing:
        return {
            "check":   check_name,
            "status":  "warn",
            "message": f"Could not run check — missing columns: {missing}",
            "details": [],
        }

    for idx, row in df.iterrows():
        v20   = row[col_20]
        v40   = row[col_40]
        v40hc = row[col_40hc]

        # Skip rows with any null value
        if pd.isna(v20) or pd.isna(v40) or pd.isna(v40hc):
            continue

        # 20' should be less than 40'
        if v20 >= v40:
            details.append({
                "row":      idx + 2,
                "column":   f"{col_20} vs {col_40}",
                "value":    f"{v20} >= {v40}",
                "expected": f"20' < 40'",
            })

        # 20' should be less than 40HC
        if v20 >= v40hc:
            details.append({
                "row":      idx + 2,
                "column":   f"{col_20} vs {col_40hc}",
                "value":    f"{v20} >= {v40hc}",
                "expected": f"20' < 40HC",
            })

        # 40' should be less than or equal to 40HC
        if v40 > v40hc:
            details.append({
                "row":      idx + 2,
                "column":   f"{col_40} vs {col_40hc}",
                "value":    f"{v40} > {v40hc}",
                "expected": f"40' <= 40HC",
            })

    return _make_result(
        check_name,
        details,
        pass_message=f"All size relationships are correct (20' < 40' <= 40HC).",
        fail_message_fn=lambda d: f"{len(d)} row(s) violate the expected size relationships.",
    )


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

    # Missing columns are a warn, not a fail
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

    return _make_result(
        check_name,
        details,
        pass_message="All columns contain the expected data types.",
        fail_message_fn=lambda d: (
            f"{len(d)} type violation(s) found across "
            f"{len({x['column'] for x in d})} column(s)."
        ),
    )


# ---------------------------------------------------------------------------
# Check 2: ALL IN totals are greater than zero and not null
# ---------------------------------------------------------------------------

def check_all_in_positive_and_nonnull(df: pd.DataFrame) -> dict:
    """
    Validates that 20' ALL IN, 40' ALL IN, and 40HC ALL IN are:
      - Not null
      - Greater than zero
    A zero or missing all-in rate almost certainly indicates a data entry problem.
    """
    check_name  = "ALL IN Totals — Non-Null and Greater Than Zero"
    all_in_cols = ["20' ALL IN", "40' ALL IN", "40HC ALL IN"]
    details     = []

    for col in all_in_cols:
        if col not in df.columns:
            continue

        for idx, value in enumerate(df[col]):
            if pd.isna(value):
                details.append({
                    "row":      idx + 2,
                    "column":   col,
                    "value":    "NULL",
                    "expected": "> 0 and not null",
                })
            elif value <= 0:
                details.append({
                    "row":      idx + 2,
                    "column":   col,
                    "value":    value,
                    "expected": "> 0 and not null",
                })

    return _make_result(
        check_name,
        details,
        pass_message="All ALL IN totals are present and greater than zero.",
        fail_message_fn=lambda d: f"{len(d)} row(s) have a null or zero ALL IN total.",
    )


# ---------------------------------------------------------------------------
# Check 3: Effective Date is before End Date
# ---------------------------------------------------------------------------

def check_effective_before_end_date(df: pd.DataFrame) -> dict:
    """
    Validates that EFFECTIVE DATE is always earlier than or equal to END DATE.
    Skips rows where either date is null — that's caught by the nulls check.
    """
    check_name = "Effective Date Before End Date"

    if "EFFECTIVE DATE" not in df.columns or "END DATE" not in df.columns:
        return {
            "check":   check_name,
            "status":  "warn",
            "message": "EFFECTIVE DATE or END DATE column not found in file.",
            "details": [],
        }

    details = []
    for idx, row in df.iterrows():
        eff = row["EFFECTIVE DATE"]
        end = row["END DATE"]

        if pd.isna(eff) or pd.isna(end):
            continue

        if eff > end:
            details.append({
                "row":      idx + 2,
                "column":   "EFFECTIVE DATE / END DATE",
                "value":    f"{eff.date()} > {end.date()}",
                "expected": "EFFECTIVE DATE <= END DATE",
            })

    return _make_result(
        check_name,
        details,
        pass_message="All effective dates fall before their end dates.",
        fail_message_fn=lambda d: f"{len(d)} row(s) where EFFECTIVE DATE is later than END DATE.",
    )


# ---------------------------------------------------------------------------
# Check 4: ALL IN size relationships — 20' < 40' <= 40HC
# ---------------------------------------------------------------------------

def check_all_in_size_relationships(df: pd.DataFrame) -> dict:
    """
    Validates the expected pricing relationship between container sizes
    for ALL IN totals: 20' < 40' <= 40HC.
    """
    return _check_size_relationships(
        df,
        col_20   = "20' ALL IN",
        col_40   = "40' ALL IN",
        col_40hc = "40HC ALL IN",
        check_name = "ALL IN Size Relationships (20' < 40' <= 40HC)",
    )


# ---------------------------------------------------------------------------
# Check 5: Ocean Base Charge size relationships — 20' < 40' <= 40HC
# ---------------------------------------------------------------------------

def check_ocean_base_size_relationships(df: pd.DataFrame) -> dict:
    """
    Validates the expected pricing relationship between container sizes
    for Ocean Freight Base Charges: 20' < 40' <= 40HC.
    """
    return _check_size_relationships(
        df,
        col_20   = "20' Ocean Freight Base Charge",
        col_40   = "40' Ocean Freight Base Charge",
        col_40hc = "40HC Ocean Freight Base Charge",
        check_name = "Ocean Base Charge Size Relationships (20' < 40' <= 40HC)",
    )