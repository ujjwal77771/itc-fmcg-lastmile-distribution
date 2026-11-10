"""
Verify all cell references and formula syntax in model/itc_model.xlsx
"""
import openpyxl
import re

wb = openpyxl.load_workbook(r"c:\Users\BIT\OneDrive\Desktop\ANTIGRAVITY BACKUP\scratch\itc-lastmile-project\model\itc_model.xlsx", data_only=False)

sheet_names = wb.sheetnames
print(f"Loaded workbook with {len(sheet_names)} sheets: {sheet_names}")

errors = []
total_formulas = 0

for sname in sheet_names:
    ws = wb[sname]
    for r in range(1, ws.max_row + 1):
        for c in range(1, ws.max_column + 1):
            val = ws.cell(row=r, column=c).value
            if val and str(val).startswith('='):
                total_formulas += 1
                f_str = str(val)
                # Check for common broken references
                if "#REF!" in f_str or "#VALUE!" in f_str or "#NAME?" in f_str:
                    errors.append((sname, r, c, f_str, "Broken error literal in formula"))
                
                # Check cross-sheet references: SheetName!Cell
                matches = re.findall(r"([A-Za-z0-9_]+)!(\$?[A-Z]+\$?[0-9]+)", f_str)
                for ref_sheet, ref_cell in matches:
                    if ref_sheet not in sheet_names:
                        errors.append((sname, r, c, f_str, f"Referenced sheet '{ref_sheet}' does not exist"))

print(f"Total formulas scanned: {total_formulas}")
if errors:
    print(f"Found {len(errors)} errors:")
    for err in errors:
        print(err)
else:
    print("SUCCESS: 0 broken sheet references across all formulas!")
