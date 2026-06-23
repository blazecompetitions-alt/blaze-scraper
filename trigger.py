from flask import Flask
import blaze_scraper

app = Flask(__name__)

@app.route("/")
def home():
    return "Blaze scraper is running"

@app.route("/run")
def run_script():
    try:
        blaze_scraper.main()
        return "✅ Sheet updated successfully"
    except Exception as e:
        return f"❌ Error: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
