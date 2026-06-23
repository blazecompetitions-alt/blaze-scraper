import requests
import pandas as pd
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

def main():
    # ========================
    # GET DATA
    # ========================
    url = "https://blazecompetitions.co.uk/api/competitions?page=1&limit=100"
    response = requests.get(url)
    data = response.json()["data"]

    df = pd.DataFrame(data)

    # ========================
    # GOOGLE SHEETS AUTH
    # ========================
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = json.loads(os.environ["GOOGLE_CREDS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    # ========================
    # UPDATE SHEET
    # ========================
    sheet = client.open("Blaze Tracker").worksheet("Raw Data")

    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

    print("✅ Google Sheet updated")

# This lets it run via cron OR trigger
if __name__ == "__main__":
    main()
