import gspread
from gspread_formatting import *

# Connect to Google Sheets (This assumes your credentials.json is in your project folder)
try:
    gc = gspread.service_account(filename='credentials.json')
except FileNotFoundError:
    print("Error: Please ensure your 'credentials.json' file is in the same folder.")
    exit()

# Create the new Trading Journal
print("Building your journal. Please wait...")
sh = gc.create('AI Trading Journal - Auto')
ws = sh.sheet1
ws.update_title('September 2026')

# Add Headers on Row 5
headers = ["Date", "Asset", "Direction", "Profit/Loss", "Equity", "Bot Vision"]
ws.insert_row(headers, 5)

# Apply Green and Red color coding to the Profit/Loss column (Column D)
rules = get_conditional_format_rules(ws)

# Green for Wins (>0)
rule_win = ConditionalFormatRule(
    ranges=[GridRange.from_a1_range('D6:D1000', ws)],
    booleanRule=BooleanRule(
        condition=BooleanCondition('NUMBER_GREATER', ['0']),
        format=CellFormat(backgroundColor=Color(0.7, 0.9, 0.7))
    )
)

# Red for Losses (<0)
rule_loss = ConditionalFormatRule(
    ranges=[GridRange.from_a1_range('D6:D1000', ws)],
    booleanRule=BooleanRule(
        condition=BooleanCondition('NUMBER_LESS', ['0']),
        format=CellFormat(backgroundColor=Color(0.9, 0.7, 0.7))
    )
)

rules.append(rule_win)
rules.append(rule_loss)
rules.save()

print(f"\nSuccess! Your pre-formatted journal is ready here:\n{sh.url}")
print("Note: Remember to share this sheet with your Google Service Account email so the bot can edit it.")