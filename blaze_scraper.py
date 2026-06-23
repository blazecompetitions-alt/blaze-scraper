import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dateutil import parser

# ================= SCRAPER =================

url = "https://blazecompetitions.co.uk/api/competitions?page=1&limit=100"

def fetch_data(url):
    for i in range(3):  # try 3 times
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️ Attempt {i+1} failed: {e}")
            time.sleep(2)
    print("❌ Failed to fetch data after 3 attempts")
    return None

data = fetch_data(url)

if not data or "data" not in data:
    print("❌ No valid data received - stopping")
    exit()

results = []

for comp in data["data"]:
    if comp["status"] != "ACTIVE":
        continue

    # Fix time (+1 hour UK)
    end_date = parser.parse(comp["endDate"]) + timedelta(hours=1)

    results.append({
        "Title": comp["title"],
        "End Date": end_date,
        "Price": float(comp["pricePerTicket"]),
        "Tickets Sold": comp["ticketsSold"],
        "Max Tickets": comp["maxTickets"],
        "URL": f"https://blazecompetitions.co.uk/competition/{comp['slug']}"
    })

# stop if no data
if not results:
    print("❌ No ACTIVE competitions found")
    exit()

# ==================== DATAFRAME ====================

df = pd.DataFrame(results)

# % sold (as a proper percentage)
df["% Sold"] = (df["Tickets Sold"] / df["Max Tickets"])
df["% Sold"] = df["% Sold"].round(2)

# ensure datetime (important for sorting)df["End Date"] = pd.to_datetime(df["End Date"])

# sort properly by real datetime
df = df.sort_values(by="End Date", ascending=True)

# format date for display AFTER sorting
df["End Date"] = df["End Date"].dt.strftime("%A %d %B %Y %H:%M")

# reorder columns
df = df[
    [
        "Title",
        "End Date",
        "Price",
        "Tickets Sold",
        "Max Tickets",
        "% Sold",
        "URL"
    ]
]

# ================= GOOGLE SHEETS =================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

import os
import json
from oauth2client.service_account import ServiceAccountCredentials

creds_dict = json.loads(os.environ["GOOGLE_CREDS"])

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)

sheet = client.open("Blaze Tracker").worksheet("Raw Data")

sheet.clear()
sheet.update([df.columns.values.tolist()] + df.values.tolist())

print("✅ Google Sheet updated")

# ================== CLEAN DATA ==================

df = df.replace([float("inf"), -float("inf")], 0)
df = df.fillna(0)

# ================== GOOGLE SHEETS ==================

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "/Users/Ryan-AnnFinance/blaze/creds.json",
    scope
)

client = gspread.authorize(creds)

sheet = client.open("Blaze Tracker").worksheet("Raw Data")

# Convert to string just before upload

# Upload
sheet.clear()
sheet.update([df.columns.values.tolist()] + df.values.tolist())

print("✅ Google Sheet updated")

