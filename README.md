# Transportation Report Sanity Checks

A lightweight Python tool that automatically validates the weekly Transportation
Report Excel file. It checks that the data is correct, complete, and consistent
before the report is used for analysis or distribution.

---

## What It Does

Every time you run it, the tool will:

1. Automatically find the latest Transportation Report in the configured folder
2. Load it into memory
3. Run a series of sanity checks against the data
4. Print a formatted report showing what passed, failed, or needs attention

---

## Project Structure

```
sanity_checks/
  main.py             Entry point — run this to execute all checks
  checks.py           All sanity check functions live here
  schema.py           Defines the expected data type for every column
  config.py           Settings: folder path, output options
  reporter.py         Formats and prints results to the console or log file
  requirements.txt    Python dependencies
  README.md           This file
```

---

## Setup

**Requirements:** Python 3.8+

**1. Create and activate a virtual environment:**
```bash
python -m venv venv
source venv/Scripts/activate    # Windows (Git Bash)
source venv/bin/activate        # Mac / Linux
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Set your report folder path in `config.py`:**
```python
REPORT_FOLDER = r"\\Corpnas\UserData\Data\cp_imports_operations\Transportation reports"
```
This only needs to be set once. The tool will always find the latest report
in that folder automatically — no need to update the filename each week.

---

## Running the Checks

```bash
python main.py
```

That's it. The tool finds the latest file, runs all checks, and prints results.

---

## Reading the Output

```
============================================================
  SANITY CHECK REPORT
  Run at: 2026-06-03 14:22:10
============================================================
  Total checks : 3
  Passed       : 2
  Failed       : 1
  Warnings     : 0
============================================================

  ✅ PASS  Column Type Validation
           All columns contain the expected data types.

  ❌ FAIL  Effective Date Before End Date
           4 row(s) where Effective Date is later than End Date.

           ROW    COLUMN                  VALUE        EXPECTED
           ----   ----------------------  -----------  --------
           14     Effective Date          2026-07-01   < End Date

============================================================
  ❌ One or more checks failed. Review above.
============================================================
```

- **✅ PASS** — check ran cleanly, no issues found
- **❌ FAIL** — data problem found, row-level detail shown below
- **⚠️  WARN** — something unexpected but not necessarily wrong (e.g. a column was renamed)

Row numbers in the output correspond directly to row numbers in the Excel file.

---

## Adding a New Check

**1.** Write a new function in `checks.py`. Every check follows this pattern:

```python
def check_your_check_name(df: pd.DataFrame) -> dict:
    # your logic here
    failures = df[df["Column A"] > df["Column B"]]

    if failures.empty:
        return {
            "check":   "Your Check Name",
            "status":  "pass",
            "message": "All values look good.",
            "details": []
        }
    return {
        "check":   "Your Check Name",
        "status":  "fail",
        "message": f"{len(failures)} row(s) failed.",
        "details": [
            {"row": idx + 2, "column": "Column A", "value": row["Column A"], "expected": "< Column B"}
            for idx, row in failures.iterrows()
        ]
    }
```

**2.** Register it in `main.py` by adding it to the `CHECKS` list:

```python
from checks import check_column_types, check_your_check_name

CHECKS = [
    check_column_types,
    check_your_check_name,
]
```

That's all — it will run automatically on the next execution.

---

## Configuration Options

All settings are in `config.py`:

| Setting | Default | Description |
|---|---|---|
| `REPORT_FOLDER` | *(your network path)* | Folder scanned for the latest report |
| `SHEET_NAME` | `0` | Sheet to read — `0` means the first sheet |
| `SHOW_DETAILS` | `True` | Print row-level detail for failures |
| `WRITE_LOG` | `False` | Save results to a log file |
| `LOG_FILE_PATH` | `sanity_check.log` | Path for the log file if enabled |

---

## Updating the Column Schema

If columns are added, removed, or renamed in the source report, update `schema.py`.
Each entry maps a column name to its expected type:

```python
"Effective Date":   "date",
"Carrier Type":     "string",
"20' ALL IN":       "numeric",
```

Valid types: `"date"`, `"string"`, `"numeric"`, `"boolean"`

---

## Dependencies

| Package | Purpose |
|---|---|
| `pandas` | Reads the Excel file and powers all data checks |
| `openpyxl` | Engine pandas uses to open `.xlsx` files |


## pending new updates..
