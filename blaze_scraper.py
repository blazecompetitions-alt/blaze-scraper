import os
import json
from datetime import datetime

import gspread
import pandas as pd
import requests
from oauth2client.service_account import ServiceAccountCredentials

print("🚀 Running Blaze scraper...")

# ======================================
# GOOGLE SHEETS
# ======================================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(os.environ["GOOGLE_CREDS"]),
    scope,
)

client = gspread.authorize(creds)

sheet = client.open("Blaze Tracker").worksheet("Raw Data")

# ======================================
# DOWNLOAD DATA
# ======================================

url = "https://blazecompetitions.co.uk/api/competitions?page=1&limit=100"

try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

except Exception as e:
    print("❌ API ERROR:", e)
    raise

# ======================================
# FIND COMPETITIONS
# ======================================

comps = []

if isinstance(data, list):
    comps = data

elif isinstance(data, dict):

    if isinstance(data.get("competitions"), list):
        comps = data["competitions"]

    elif isinstance(data.get("data"), list):
        comps = data["data"]

    elif isinstance(data.get("data"), dict):
        comps = data["data"].get("competitions", [])

print(f"✅ Found {len(comps)} competitions")

# ======================================
# HELPERS
# ======================================

def get_price(comp):

    possible_prices = [
        comp.get("ticketPrice"),
        comp.get("price"),
        comp.get("ticket", {}).get("price"),
    ]

    prices = comp.get("prices")

    if isinstance(prices, list) and prices:
        possible_prices.append(prices[0].get("price"))

    for p in possible_prices:
        if p not in [None, ""]:
            try:
                return f"£{float(p):.2f}"
            except:
                return str(p)

    return ""

def get_end_date(comp):

    end = (
        comp.get("endDate")
        or comp.get("end_date")
        or comp.get("drawDate")
        or comp.get("draw_date")
    )

    if not end:
        return ""

    try:
        dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
        return dt.strftime("%A %d/%m/%Y %H:%M")
    except:
        return end

# ======================================
# BUILD ROWS
# ======================================

rows = []

for comp in comps:

    try:

        title = comp.get("title", "")

        price = get_price(comp)

        end_date = get_end_date(comp)

        tickets_sold = (
            comp.get("ticketsSold")
            or comp.get("tickets_sold")
            or 0
        )

        max_tickets = (
            comp.get("maxTickets")
            or comp.get("max_tickets")
            or 0
        )

        try:
            percent = round((tickets_sold / max_tickets) * 100, 1) if max_tickets else 0
        except:
            percent = 0

        slug = comp.get("slug", "")

        url_link = (
            f"https://blazecompetitions.co.uk/competition/{slug}"
            if slug
            else ""
        )

        rows.append([
            title,
            end_date,
            price,
            tickets_sold,
            max_tickets,
            f"{percent}%",
            url_link,
        ])

    except Exception as e:
        print("❌ Error processing competition:", e)

# ======================================
# DATAFRAME
# ======================================

df = pd.DataFrame(
    rows,
    columns=[
        "Title",
        "End Date",
        "Price",
        "Tickets Sold",
        "Max Tickets",
        "% Sold",
        "URLs",
    ],
)

df = df.fillna("")

# ======================================
# UPDATE GOOGLE SHEET
# ======================================

if len(rows) == 0:
    print("❌ No competitions found.")
    raise Exception("No data returned from API.")

sheet.clear()

sheet.update(
    [df.columns.tolist()] + df.values.tolist()
)

print(f"✅ Updated Google Sheet with {len(rows)} competitions.")
