import requests
import pandas as pd
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

print("🚀 VERSION 6 LIVE")

# ======================
# FETCH DATA
# ======================

url = "https://blazecompetitions.co.uk/api/competitions?page=1&limit=100"
response = requests.get(url)
data = response.json()

rows = []

# ======================
# PARSE DATA
# ======================

for comp in data.get("data", []):
    try:
        # BASIC INFO
        title = comp.get("title", "")
        price = comp.get("price", "")

        # 🔥 CORRECT FIELDS (confirmed working structure)
        sold = comp.get("ticketsSold", 0)

        max_tickets = (
            comp.get("maxTickets") or
            comp.get("max_entries") or
            comp.get("maxEntries") or
            0
        )

        # % SOLD
        try:
            percent_sold = round((int(sold) / int(max_tickets)) * 100, 1) if int(max_tickets) > 0 else ""
        except:
            percent_sold = ""

        # DATE (SAFE + CLEAN)
        end_date_raw = comp.get("endDate", "")
        try:
            dt = datetime.fromisoformat(end_date_raw.replace("Z", ""))
            end_date = dt.strftime("%d/%m/%Y %H:%M")
        except:
            end_date = end_date_raw

        # URL
        slug = comp.get("slug", "")
        url_link = f"https://blazecompetitions.co.uk/competition/{slug}" if slug else ""

        rows.append({
            "Title": title,
            "End Date": end_date,
            "Price (£)": price,
            "Tickets Sold": sold,
            "Max Tickets": max_tickets,
            "% Sold": percent_sold,
            "URLs": url_link
        })

    except Exception as e:
        print("❌ Error parsing row:", e)

# ======================
# DATAFRAME CLEAN
# ======================

df = pd.DataFrame(rows)

df = df.fillna("")        # remove NaN
df = df.astype(str)       # force strings (prevents JSON errors)

# ======================
# GOOGLE SHEETS
# ======================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)
sheet = client.open("Blaze Tracker").worksheet("Raw Data")

# CLEAR + UPDATE
sheet.clear()
sheet.update([df.columns.values.tolist()] + df.values.tolist())

print("✅ Sheet updated successfully")
