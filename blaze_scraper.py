import requests
import pandas as pd
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

print("🚀 VERSION 5 LIVE")

url = "https://blazecompetitions.co.uk/api/competitions?page=1&limit=100"
response = requests.get(url)
data = response.json()

rows = []

for comp in data.get("data", []):
    try:
        title = comp.get("title", "")

        # PRICE
        price = comp.get("price", "")

        # MAX TICKETS (try multiple keys)
        max_tickets = (
            comp.get("maxTickets") or
            comp.get("max_tickets") or
            comp.get("maxEntries") or
            ""
        )

        # SOLD
        sold = (
            comp.get("ticketsSold") or
            comp.get("soldTickets") or
            0
        )

        # % SOLD
        try:
            percent_sold = round((int(sold) / int(max_tickets)) * 100, 1) if max_tickets else ""
        except:
            percent_sold = ""

        # DATE (FIXED PROPERLY)
        end_date_raw = comp.get("endDate")
        if end_date_raw:
            try:
                dt = datetime.fromisoformat(end_date_raw.replace("Z", ""))
                end_date = dt.strftime("%d/%m/%Y %H:%M")
            except:
                end_date = end_date_raw
        else:
            end_date = ""

        # URL
        slug = comp.get("slug", "")
        url_link = f"https://blazecompetitions.co.uk/competition/{slug}" if slug else ""

        rows.append({
            "Title": title,
            "End Date": end_date,
            "Price (£)": price,
            "Max Tickets": max_tickets,
            "Sold": sold,
            "% Sold": percent_sold,
            "URL": url_link
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
