import requests
import pandas as pd
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

print("🚀 Running Blaze scraper...")

# ========================
# GOOGLE SHEETS SETUP
# ========================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open("Blaze Tracker").worksheet("Raw Data")

# ========================
# API CALL
# ========================

url = "https://blazecompetitions.co.uk/api/competitions?page=1&limit=100"
response = requests.get(url)
data = response.json()

print("RAW TYPE:", type(data))

# ========================
# HANDLE API STRUCTURE
# ========================

comps = []

if isinstance(data, list):
    comps = data

elif isinstance(data, dict):
    if "competitions" in data:
        comps = data["competitions"]

    elif "data" in data:
        if isinstance(data["data"], list):
            comps = data["data"]
        elif isinstance(data["data"], dict):
            comps = data["data"].get("competitions", [])

print("TOTAL COMPS:", len(comps))

# ✅ THIS WAS MISSING BEFORE
rows = []

# ========================
# PROCESS DATA
# ========================

for comp in comps:
    try:
        title = comp.get("title", "")

        # DATE
        end_raw = comp.get("endDate")
        if end_raw:
            dt = datetime.fromisoformat(end_raw.replace("Z", "+00:00"))
            end_date = dt.strftime("%A %d/%m/%Y %H:%M")
        else:
            end_date = ""

        # ========================
# PRICE (FULL SAFE VERSION)
# ========================

price = ""

try:
    if comp.get("ticketPrice"):
        raw_price = comp.get("ticketPrice")

    elif comp.get("price"):
        raw_price = comp.get("price")

    elif comp.get("ticket", {}).get("price"):
        raw_price = comp.get("ticket", {}).get("price")

    elif comp.get("prices") and isinstance(comp["prices"], list):
        raw_price = comp["prices"][0].get("price")

    else:
        raw_price = None

    if raw_price:
        price = f"£{float(raw_price):.2f}"

except Exception as e:
    print("❌ Price error:", e)
    
        # TICKETS
        tickets_sold = comp.get("ticketsSold", 0)
        max_tickets = comp.get("maxTickets", 0)

        # % SOLD
        try:
            percent = round((tickets_sold / max_tickets) * 100, 1) if max_tickets else 0
            percent_sold = f"{percent}%"
        except:
            percent_sold = "0%"

        # URL
        slug = comp.get("slug", "")
        url_link = f"https://blazecompetitions.co.uk/competition/{slug}" if slug else ""

        rows.append([
            title,
            end_date,
            price,
            tickets_sold,
            max_tickets,
            percent_sold,
            url_link
        ])

    except Exception as e:
        print("❌ Error processing comp:", e)

# ========================
# DATAFRAME
# ========================

df = pd.DataFrame(rows, columns=[
    "Title",
    "End Date",
    "Price",
    "Tickets Sold",
    "Max Tickets",
    "% Sold",
    "URLs"
])

df = df.fillna("")

# ========================
# SAFE UPDATE
# ========================

if len(rows) > 0:
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("✅ Google Sheet updated")
else:
    print("❌ No data returned — sheet NOT cleared")
