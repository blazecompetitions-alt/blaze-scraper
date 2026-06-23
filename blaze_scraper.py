import requests
import pandas as pd
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

print("🚀 VERSION 7 LIVE")

url = "https://blazecompetitions.co.uk/api/competitions?page=1&limit=100"
response = requests.get(url)
data = response.json()

rows = []

for comp in data.get("data", []):
    try:
        title = comp.get("title", "")

        # ✅ CORRECT PRICE FIELD
        price = comp.get("ticketPrice", "")

        # ✅ USE MATCHING VALUES
        max_tickets = comp.get("maxTickets", 0)
        sold = comp.get("ticketsSold", 0)

        # FIX: prevent nonsense values
        if sold > max_tickets:
            sold = max_tickets

        # ✅ % SOLD WITH %
        try:
            percent_sold = f"{round((sold / max_tickets) * 100, 1)}%" if max_tickets else ""
        except:
            percent_sold = ""

        # ✅ FIX TIMEZONE (UTC → UK)
        end_date_raw = comp.get("endDate", "")
        try:
            dt = datetime.fromisoformat(end_date_raw.replace("Z", ""))
            dt = dt + timedelta(hours=1)  # 🔥 UK FIX
            end_date = dt.strftime("%d/%m/%Y %H:%M")
        except:
            end_date = end_date_raw

        # ✅ URL
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
        print("Error parsing:", e)

df = pd.DataFrame(rows)

# CLEAN DATA
df = df.fillna("")
df = df.astype(str)

# GOOGLE SHEETS
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

print("✅ Sheet updated")
