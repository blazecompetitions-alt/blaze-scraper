from flask import Flask
import subprocess

app = Flask(__name__)

@app.route("/run")
def run_script():
    try:
        blaze_scraper.main()   # 👈 call function directly
        return "✅ Sheet updated successfully"
    except Exception as e:
        return f"❌ Error: {e}"

@app.route("/")
def home():
    return "Blaze scraper is running"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
