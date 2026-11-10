"""
Inspect exact targets of cross-sheet references
"""
import openpyxl

wb = openpyxl.load_workbook(r"c:\Users\BIT\OneDrive\Desktop\ANTIGRAVITY BACKUP\scratch\itc-lastmile-project\model\itc_model.xlsx")

def print_sheet_rows(sname, max_r=40):
    ws = wb[sname]
    print(f"=== {sname} ===")
    for r in range(1, max_r + 1):
        vals = [f"Col{c}:{ws.cell(row=r, column=c).value}" for c in range(1, min(ws.max_column+1, 8)) if ws.cell(row=r, column=c).value is not None]
        if vals:
            print(f"R{r}: " + " | ".join(vals[:4]))

print_sheet_rows("Assumptions_Inputs", 38)
