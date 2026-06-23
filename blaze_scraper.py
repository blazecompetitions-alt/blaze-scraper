import requests
import pandas as pd
import numpy as np
import gspread
import os
import json

from oauth2client.service_account import ServiceAccountCredentials

# ========================
# CONFIG
# ========================

URL = "https://blazecompetitions.co.uk/api/competitions?page=1&limit=100"

SHEET_NAME = "Blaze Tracker"
WORKSHEET_NAME = "Raw Data"

# ========================
# MAIN SCRAPER FUNCTION
# ========================

def main():
    print("🚀 Running Blaze scraper...")

    # ------------------------
    # GET DATA FROM API
    # ------------------------
    response = requests.get(URL)
    data = response.json()

    competitions = data.get("data", [])

    if not competitions:
        print("⚠️ No competitions found")
        return

    # ------------------------
    # CONVERT TO DATAFRAME
    # ------------------------
    df = pd.json_normalize(competitions)

    # ------------------------
    # CLEAN DATA (CRITICAL FIXES)
    # ------------------------

    # Replace NaN + infinities
    df = df.replace([np.nan, np.inf, -np.inf], "")

    # Convert EVERYTHING to string (fixes nested JSON issue)
    df = df.astype(str)

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
    # OPEN SHEET
    # ------------------------

    sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

    # ------------------------
    # UPDATE SHEET
    # ------------------------

    sheet.clear()

    sheet.update([df.columns.values.tolist()] + df.values.tolist())

    print("✅ Google Sheet updated successfully")


# ========================
# RUN LOCALLY (OPTIONAL)
# ========================

if __name__ == "__main__":
    main()
