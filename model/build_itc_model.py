"""
ITC FMCG Last-Mile Distribution Model Generator
Builds model/itc_model.xlsx adhering strictly to all 9 supply chain modeling rules:
1. Periodic-review safety stock formula with stochastic demand & lead time
2. Vehicle capacity and weight/volume utilization with MIN(capacity, orders)
3. Total delivered cost build including linehaul, hub handling, rent, holding, milk-run, distance matrix & circuity factor
4. Incremental cases formula flagged as WEAKEST ASSUMPTION
5. Formula-driven scenario sensitivity (No Excel data tables)
6. All sample values flagged "ILLUSTRATIVE - replace with field data"
7. OTIF, days of cover, and transporter scorecard
8. Compliance sheet with blank legal rule column
9. Color coding: Blue inputs, Black local formulas, Green cross-sheet links, units on every input, zero formula errors, PASS/FAIL checks.
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
# remove default sheet
wb.remove(wb.active)

# ----------------- STYLES -----------------
FONT_NAME = "Calibri"

# Colors
COLOR_BLUE_INPUT = "002060"    # Dark Blue for inputs
COLOR_BLACK_FORMULA = "000000" # Black for local formulas
COLOR_GREEN_LINK = "006100"    # Green for cross-sheet links
COLOR_WHITE = "FFFFFF"
COLOR_GRAY_TEXT = "595959"

# Fills
FILL_HEADER = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid") # Corporate Dark Blue
FILL_SUBHEADER = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid") # Soft blue
FILL_ACCENT = PatternFill(start_color="F2DCDB", end_color="F2DCDB", fill_type="solid") # Soft red/coral for flags
FILL_ZEBRA = PatternFill(start_color="F9FBFD", end_color="F9FBFD", fill_type="solid")
FILL_PASS = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
FILL_FAIL = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

# Fonts
font_title = Font(name=FONT_NAME, size=16, bold=True, color="1F497D")
font_subtitle = Font(name=FONT_NAME, size=10, italic=True, color=COLOR_GRAY_TEXT)
font_sec_hdr = Font(name=FONT_NAME, size=12, bold=True, color=COLOR_WHITE)
font_sub_hdr = Font(name=FONT_NAME, size=10, bold=True, color="1F497D")
font_tbl_hdr = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_WHITE)
font_regular = Font(name=FONT_NAME, size=10, color=COLOR_BLACK_FORMULA)
font_bold = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_BLACK_FORMULA)
font_input = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_BLUE_INPUT)
font_formula = Font(name=FONT_NAME, size=10, color=COLOR_BLACK_FORMULA)
font_link = Font(name=FONT_NAME, size=10, color=COLOR_GREEN_LINK)
font_flag = Font(name=FONT_NAME, size=9, bold=True, color="9C0006")
font_pass = Font(name=FONT_NAME, size=10, bold=True, color="006100")
font_fail = Font(name=FONT_NAME, size=10, bold=True, color="9C0006")

# Borders
thin_line = Side(style='thin', color="D9D9D9")
double_line = Side(style='double', color="1F497D")
thick_top = Side(style='thin', color="1F497D")

border_cell = Border(left=thin_line, right=thin_line, top=thin_line, bottom=thin_line)
border_total = Border(top=thick_top, bottom=double_line)

align_left = Alignment(horizontal='left', vertical='center')
align_right = Alignment(horizontal='right', vertical='center')
align_center = Alignment(horizontal='center', vertical='center')

def apply_title_block(ws, title, subtitle):
    ws['A1'] = title
    ws['A1'].font = font_title
    ws['A2'] = subtitle
    ws['A2'].font = font_subtitle
    ws['A3'] = "ILLUSTRATIVE MODEL - Replace sample parameters with verified district/field data"
    ws['A3'].font = font_flag
    ws.row_dimensions[1].height = 24
    ws.row_dimensions[2].height = 18
    ws.row_dimensions[3].height = 16

def auto_fit_columns(ws, min_width=12):
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            val = str(cell.value or '')
            if cell.number_format and '%' in cell.number_format:
                val += '%'
            if val.startswith('='):
                val = "1234567.89" # proxy length
            max_len = max(max_len, len(val))
        ws.column_dimensions[col_letter].width = max(max_len + 3, min_width)

print("Building workbook...")
