import os
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)
APP_STATUS = os.environ.get("APP_STATUS", "stable")

with open("index.html", "r") as f:
    HTML_TEMPLATE = f.read()

@app.route("/")
def index():
    page_content = HTML_TEMPLATE
    if APP_STATUS == "faulty":
        page_content = page_content.replace("System Status: Stable (v1.0.0)", "System Status: CRASHED (v1.1.0-faulty)")
        page_content = page_content.replace('const urlParams = new URLSearchParams(window.location.search);', 'const urlParams = new URLSearchParams("status=faulty");')
    return render_template_string(page_content)

@app.route("/health")
def health():
    if APP_STATUS == "faulty":
        return jsonify({"status": "DOWN", "reason": "Simulated fault."}), 500
    return jsonify({"status": "UP", "release": "stable"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
