# main.py
# Entry point for the sanity check runner.
# Run this file to validate your Excel report:
#
#   python main.py
#
# Configure the file path and output options in config.py.

import sys
import pandas as pd

import config
from checks import (
    check_column_types,
    check_all_in_positive_and_nonnull,
    check_effective_before_end_date,
    check_all_in_size_relationships,
)
from reporter import print_report, write_log


# ---------------------------------------------------------------------------
# Register all checks here — add new ones to this list as you build them
# ---------------------------------------------------------------------------

CHECKS = [
    check_all_in_positive_and_nonnull,
    check_effective_before_end_date,
    check_all_in_size_relationships,
    check_column_types,
]


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def load_file(path: str, sheet) -> pd.DataFrame:
    """Loads the Excel file and returns a dataframe. Exits cleanly on failure."""
    try:
        df = pd.read_excel(path, sheet_name=sheet)
        print(f"\n  Loaded: {path} — {len(df)} rows, {len(df.columns)} columns")
        return df
    except FileNotFoundError:
        print(f"\n  ❌ File not found: {path}")
        print("     Check the EXCEL_FILE_PATH setting in config.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n  ❌ Could not read file: {e}")
        sys.exit(1)


def run_checks(df: pd.DataFrame) -> list:
    """Runs all registered checks and returns their results."""
    results = []
    for check_fn in CHECKS:
        result = check_fn(df)
        results.append(result)
    return results


def main():
    df      = load_file(config.EXCEL_FILE_PATH, config.SHEET_NAME)
    results = run_checks(df)

    print_report(results, show_details=config.SHOW_DETAILS)

    if config.WRITE_LOG:
        write_log(results, config.LOG_FILE_PATH)

    # Exit with a non-zero code if any check failed
    any_failures = any(r["status"] == "fail" for r in results)
    sys.exit(1 if any_failures else 0)


if __name__ == "__main__":
    main()