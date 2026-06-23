from flask import Flask
import subprocess

app = Flask(__name__)

@app.route("/run")
def run_script():
    try:
        subprocess.run(["python3", "blaze_scraper.py"], check=True)
        return "✅ Sheet updated successfully"
    except Exception as e:
        return f"❌ Error: {e}"

@app.route("/")
def home():
    return "Blaze scraper is running"
