import requests
import pandas as pd
import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials

def main():
    print("🚀 NEW CLEAN VERSION RUNNING")

    url = "https://blazecompetitions.co.uk/api/competitions?page=1&limit=100"

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"API failed: {response.status_code}")

    try:
        data = response.json()
    except Exception as e:
        raise Exception(f"JSON error: {e}")

    competitions = data.get("data", [])

    if not isinstance(competitions, list):
        raise Exception("Unexpected API format")

    rows = []

    for comp in competitions:
        if not isinstance(comp, dict):
            continue

        rows.append({
            "id": str(comp.get("id", "")),
            "title": str(comp.get("title", "")),
            "price": str(comp.get("price", "")),
            "max_entries": str(comp.get("maxEntries", "")),
            "sold": str(comp.get("sold", "")),
            "status": str(comp.get("status", "")),
            "draw_date": str(comp.get("drawDate", "")),
        })

    df = pd.DataFrame(rows)

    # ✅ Completely safe cleaning
    df = df.fillna("").astype(str)

    # ------------------------
    # GOOGLE SHEETS
    # ------------------------
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = json.loads(os.environ["GOOGLE_CREDS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    sheet = client.open("Blaze Tracker").worksheet("Raw Data")

    # ⚠️ SAFE UPDATE (no list manipulation at all)
    values = [df.columns.tolist()] + df.values.tolist()

    sheet.clear()
    sheet.update(values)

    print("✅ Google Sheet updated successfully")

if __name__ == "__main__":
    main()
