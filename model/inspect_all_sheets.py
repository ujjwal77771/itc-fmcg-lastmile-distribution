"""
Inspect all sheets rows
"""
import openpyxl

wb = openpyxl.load_workbook(r"c:\Users\BIT\OneDrive\Desktop\ANTIGRAVITY BACKUP\scratch\itc-lastmile-project\model\itc_model.xlsx")

def inspect_sheet(sname):
    ws = wb[sname]
    print(f"\n==================== {sname} ====================")
    for r in range(1, ws.max_row + 1):
        row_str = []
        for c in range(1, min(ws.max_column+1, 9)):
            v = ws.cell(row=r, column=c).value
            if v is not None:
                v_s = str(v)
                if len(v_s) > 25: v_s = v_s[:22] + "..."
                row_str.append(f"C{c}:{v_s}")
        if row_str:
            print(f"R{r:2d} | " + " | ".join(row_str))

for s in ["District_Baseline", "Inventory_Logic", "Delivered_Cost_Build", "Revenue_and_Financials", "Scorecard_and_OTIF", "Checks", "Summary_Dashboard"]:
    inspect_sheet(s)
