import requests
import pandas as pd
import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials

# ------------------------
# MAIN FUNCTION (IMPORTANT)
# ------------------------
def main():
    print("🚀 Running Blaze scraper...")

    url = "https://blazecompetitions.co.uk/api/competitions?page=1&limit=100"

    response = requests.get(url)

    # ✅ SAFETY CHECK
    if response.status_code != 200:
        raise Exception(f"API failed: {response.status_code}")

    try:
        data = response.json()
    except:
        raise Exception("Invalid JSON from API")

    competitions = data.get("data", [])

    rows = []

    for comp in competitions:
        try:
            row = {
                "id": comp.get("id", ""),
                "title": comp.get("title", ""),
                "price": comp.get("price", ""),
                "max_entries": comp.get("maxEntries", ""),
                "sold": comp.get("sold", ""),
                "status": comp.get("status", ""),
                "draw_date": comp.get("drawDate", ""),
            }

            rows.append(row)

        except Exception as e:
            print(f"⚠️ Skipping bad row: {e}")
            continue

    if not rows:
        raise Exception("No data scraped")

    df = pd.DataFrame(rows)

    # ✅ FIX NaN / JSON issues
    df = df.fillna("").astype(str)

    # ------------------------
    # GOOGLE SHEETS AUTH
    # ------------------------
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = json.loads(os.environ["GOOGLE_CREDS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    client = gspread.authorize(creds)

    # ------------------------
    # UPDATE SHEET
    # ------------------------
    sheet = client.open("Blaze Tracker").worksheet("Raw Data")

    sheet.clear()

    sheet.update([df.columns.values.tolist()] + df.values.tolist())

    print("✅ Google Sheet updated")


# ------------------------
# ALLOW DIRECT RUN
# ------------------------
if __name__ == "__main__":
    main()
