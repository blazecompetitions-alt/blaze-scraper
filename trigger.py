from flask import Flask
import blaze_scraper  # ✅ IMPORTANT: no .py here

app = Flask(__name__)

# ------------------------
# HEALTH CHECK (Render needs this)
# ------------------------
@app.route("/")
def home():
    return "Blaze scraper is running ✅"

# ------------------------
# TRIGGER SCRAPER VIA URL
# ------------------------
@app.route("/run")
def run_script():
    try:
        blaze_scraper.main()   # 👈 runs your scraper
        return "✅ Sheet updated successfully"
    except Exception as e:
        return f"❌ Error: {e}"

# ------------------------
# RUN SERVER
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
