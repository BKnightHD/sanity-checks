# config.py
# Runtime settings for the sanity check runner.

import os
import re
import glob
from datetime import datetime


# ---------------------------------------------------------------------------
# Report folder — update this once, never touch it again
# ---------------------------------------------------------------------------

REPORT_FOLDER = r"\\Corpnas\UserData\Data\cp_imports_operations\Transportation reports"


# ---------------------------------------------------------------------------
# Latest file detection
# ---------------------------------------------------------------------------

def get_latest_report(folder: str) -> str:
    """
    Scans the report folder for files matching the exact pattern:
        M.D.YYYY TRANSPORTATION REPORT.xlsx
    Files with anything after "REPORT" (e.g. "(BPD & CA)") are intentionally skipped.
    Returns the full path of the file with the latest date — including future dates.
    """
    # Exact pattern: date, space, "TRANSPORTATION REPORT", nothing else before .xlsx
    EXACT_PATTERN = re.compile(
        r"^\d{1,2}\.\d{1,2}\.\d{4} TRANSPORTATION REPORT\.xlsx$",
        re.IGNORECASE
    )

    pattern  = os.path.join(folder, "*.xlsx")
    all_xlsx = glob.glob(pattern)

    # Filter to only files that match the exact naming convention
    candidates = [
        f for f in all_xlsx
        if EXACT_PATTERN.match(os.path.basename(f))
    ]

    if not candidates:
        raise FileNotFoundError(
            f"No TRANSPORTATION REPORT files found in:\n  {folder}\n"
            f"Check that REPORT_FOLDER in config.py is correct."
        )

    # Parse the date from each filename and pair it with the path
    dated_files = []
    for filepath in candidates:
        filename    = os.path.basename(filepath)
        date_str    = filename.split(" ")[0]  # grabs "x.x.xxxx" from the front
        try:
            date = datetime.strptime(date_str, "%m.%d.%Y")
            dated_files.append((date, filepath))
        except ValueError:
            # If the date doesn't parse, skip the file rather than crash
            print(f"  ⚠️  Skipping file with unrecognized date format: {filename}")
            continue

    if not dated_files:
        raise FileNotFoundError(
            "Found TRANSPORTATION REPORT files but none had a parseable date.\n"
            "Expected format: M.D.YYYY TRANSPORTATION REPORT.xlsx"
        )

    # Sort by date descending and take the first (latest)
    dated_files.sort(key=lambda x: x[0], reverse=True)
    latest_path = dated_files[0][1]

    return latest_path


# ---------------------------------------------------------------------------
# Resolved file path — this is what main.py uses
# ---------------------------------------------------------------------------

EXCEL_FILE_PATH = get_latest_report(REPORT_FOLDER)


# ---------------------------------------------------------------------------
# Other settings
# ---------------------------------------------------------------------------

SHEET_NAME      = 0
SHOW_DETAILS    = True
WRITE_LOG       = False
LOG_FILE_PATH   = "sanity_check.log"