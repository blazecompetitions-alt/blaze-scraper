import requests
import pandas as pd
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

print("🚀 VERSION 4 LIVE")

# =====================
# FETCH DATA
# =====================

url = "https://blazecompetitions.co.uk/api/competitions?page=1&limit=100"
response = requests.get(url)
data = response.json()

rows = []

for comp in data.get("data", []):
    try:
        title = comp.get("title", "")
        price = comp.get("price", "")
        max_tickets = comp.get("maxTickets", "")

        # Fix date
        end_date_raw = comp.get("endDate")
        if end_date_raw:
            try:
                end_date = datetime.fromisoformat(end_date_raw.replace("Z", "")).strftime("%d/%m/%Y %H:%M")
            except:
                end_date = ""
        else:
            end_date = ""

        rows.append({
            "Title": title,
            "End Date": end_date,
            "Price": price,
            "Max Tickets": max_tickets
        })

    except Exception as e:
        print("Error parsing row:", e)

df = pd.DataFrame(rows)

# =====================
# CLEAN DATA (CRITICAL)
# =====================

df = df.fillna("")  # REMOVE NaN
df = df.astype(str)  # FORCE STRINGS

# =====================
# GOOGLE SHEETS
# =====================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)
sheet = client.open("Blaze Tracker").worksheet("Raw Data")

sheet.clear()

sheet.update([df.columns.values.tolist()] + df.values.tolist())

print("✅ Google Sheet updated")
