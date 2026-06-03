# reporter.py
# Handles all output formatting for sanity check results.
# Nothing in this file knows about the checks themselves —
# it only knows how to display the results they return.

from datetime import datetime


# ---------------------------------------------------------------------------
# Symbols and labels
# ---------------------------------------------------------------------------

STATUS_SYMBOLS = {
    "pass": "✅ PASS",
    "fail": "❌ FAIL",
    "warn": "⚠️  WARN",
}


# ---------------------------------------------------------------------------
# Core reporter
# ---------------------------------------------------------------------------

def print_report(results: list, show_details: bool = True) -> None:
    """
    Prints a formatted sanity check report to the console.

    Args:
        results:      List of result dicts returned by check functions.
        show_details: If True, prints row-level detail for failures.
    """
    total       = len(results)
    passed      = sum(1 for r in results if r["status"] == "pass")
    failed      = sum(1 for r in results if r["status"] == "fail")
    warned      = sum(1 for r in results if r["status"] == "warn")
    timestamp   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    _print_header(timestamp, total, passed, failed, warned)

    for result in results:
        _print_result(result, show_details)

    _print_footer(failed, warned)


# ---------------------------------------------------------------------------
# Internal formatting helpers
# ---------------------------------------------------------------------------

def _print_header(timestamp, total, passed, failed, warned) -> None:
    print()
    print("=" * 60)
    print("  SANITY CHECK REPORT")
    print(f"  Run at: {timestamp}")
    print("=" * 60)
    print(f"  Total checks : {total}")
    print(f"  Passed       : {passed}")
    print(f"  Failed       : {failed}")
    print(f"  Warnings     : {warned}")
    print("=" * 60)
    print()


def _print_result(result: dict, show_details: bool) -> None:
    symbol  = STATUS_SYMBOLS.get(result["status"], "❓ UNKNOWN")
    print(f"  {symbol}  {result['check']}")
    print(f"           {result['message']}")

    # Print row-level detail for failures if requested
    if show_details and result.get("details"):
        print()
        print(f"           {'ROW':<6} {'COLUMN':<45} {'VALUE':<20} EXPECTED")
        print(f"           {'-'*4:<6} {'-'*43:<45} {'-'*18:<20} {'-'*8}")
        for d in result["details"]:
            row     = str(d["row"])
            col     = str(d["column"])[:43]   # truncate long column names
            val     = str(d["value"])[:18]    # truncate long values
            exp     = str(d["expected"])
            print(f"           {row:<6} {col:<45} {val:<20} {exp}")

    print()


def _print_footer(failed: int, warned: int) -> None:
    print("=" * 60)
    if failed == 0 and warned == 0:
        print("  ✅ All checks passed. Report looks good.")
    elif failed == 0:
        print("  ⚠️  Checks passed with warnings. Review above.")
    else:
        print("  ❌ One or more checks failed. Review above.")
    print("=" * 60)
    print()


# ---------------------------------------------------------------------------
# Optional: write results to a log file
# ---------------------------------------------------------------------------

def write_log(results: list, log_path: str) -> None:
    """
    Writes the same report to a .log file instead of (or in addition to)
    the console. Appends each run so you keep a history.
    """
    import io
    import sys

    # Capture the console output into a string
    buffer      = io.StringIO()
    old_stdout  = sys.stdout
    sys.stdout  = buffer

    print_report(results, show_details=True)

    sys.stdout  = old_stdout
    output      = buffer.getvalue()

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(output)

    print(f"  Log written to: {log_path}")