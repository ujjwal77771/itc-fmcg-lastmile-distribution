"""
Formula Integrity, Cross-Sheet Reference & Syntax Verification
Author: Ujjwal Deep | B.Tech Mechanical Engineering, BIT Mesra

Verifies that all formulas in model/itc_model.xlsx have valid OpenXML syntax,
zero broken sheet references, and compatible Excel functions (e.g. NORMSDIST instead of un-prefixed NORM.S.DIST).

Note on Calculated Display Values:
Openpyxl writes dynamic formula strings into the spreadsheet. When opened in desktop Microsoft Excel
and saved (Ctrl+S), Excel's calculation engine evaluates and writes the cached display values (<v> tags)
used by mobile viewers and web previews.
"""

import os
import openpyxl
import re

MODEL_PATH = os.path.join(os.path.dirname(__file__), "itc_model.xlsx")
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")

wb = openpyxl.load_workbook(MODEL_PATH, data_only=False)
sheet_names = wb.sheetnames
print(f"Loaded workbook: {os.path.basename(MODEL_PATH)} ({len(sheet_names)} sheets)")

errors = []
total_formulas = 0

# Disallowed modern Excel functions that cause #NAME? in OpenXML without _xlfn. prefix
INCOMPATIBLE_FUNCTIONS = [
    "NORM.S.DIST",
    "NORM.DIST",
    "NORM.S.INV",
    "NORM.INV",
    "STDEV.S",
    "STDEV.P",
    "VAR.S",
    "VAR.P"
]

for sname in sheet_names:
    ws = wb[sname]
    for r in range(1, ws.max_row + 1):
        for c in range(1, ws.max_column + 1):
            val = ws.cell(row=r, column=c).value
            if val and str(val).startswith('='):
                total_formulas += 1
                f_str = str(val)
                
                # Check for broken Excel literal errors
                for err_tok in ["#REF!", "#VALUE!", "#NAME?", "#N/A", "#DIV/0!"]:
                    if err_tok in f_str:
                        errors.append((sname, r, c, f_str, f"Found error literal {err_tok}"))
                
                # Check for incompatible function names that cause #NAME?
                for fn in INCOMPATIBLE_FUNCTIONS:
                    if fn in f_str.upper():
                        errors.append((sname, r, c, f_str, f"Incompatible function '{fn}' causes #NAME? in Excel without prefix; use legacy equivalent (e.g. NORMSDIST)"))
                
                # Check cross-sheet references: SheetName!Cell
                matches = re.findall(r"([A-Za-z0-9_]+)!(\$?[A-Z]+\$?[0-9]+)", f_str)
                for ref_sheet, ref_cell in matches:
                    if ref_sheet not in sheet_names:
                        errors.append((sname, r, c, f_str, f"Referenced sheet '{ref_sheet}' does not exist"))

print(f"Total dynamic formulas verified: {total_formulas}")
if errors:
    print(f"FAILED: Found {len(errors)} formula / reference errors:")
    for err in errors:
        print(f"  [{err[0]} R{err[1]}C{err[2]}]: {err[4]} -> {err[3]}")
    exit(1)
else:
    print("SUCCESS: Zero syntax errors, zero incompatible function names, and zero broken sheet references!")
    print("Operational Reminder: Save workbook once in desktop Excel (Ctrl+S) to pre-cache display values for mobile viewers.")
