from flask import Flask
import blaze_scraper

app = Flask(__name__)

@app.route("/")
def home():
    return "Blaze scraper is running"

@app.route("/run")
def run_script():
    try:
        print("🚀 Running Blaze scraper...")
        blaze_scraper.main()
        return "✅ Sheet updated successfully"
    except Exception as e:
        print("ERROR:", e)
        return f"❌ Error: {e}"
