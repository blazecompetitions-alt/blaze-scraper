from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/run')
def run_script():
    subprocess.run([
        "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3",
        "/Users/Ryan-AnnFinance/blaze_scraper.py"
    ])
    return "✅ Blaze scraper triggered!"

app.run(host='0.0.0.0', port=5050)
