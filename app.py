import os
from flask import Flask, jsonify

app = Flask(__name__)

COLORS = {
    "dev": "#2563eb",
    "qa": "#f97316",
    "prod": "#16a34a",
}

def get_config():
    return {
        "ambiente": os.environ.get("APP_ENV", "dev"),
        "rama": os.environ.get("GIT_BRANCH", "unknown"),
        "commit": os.environ.get("GIT_COMMIT", "unknown")[:7],
        "version": os.environ.get("APP_VERSION", "0.0.1"),
    }

@app.route("/")
def index():
    cfg = get_config()
    color = COLORS.get(cfg["ambiente"], "#6b7280")
    html = f"""
    <html>
    <head><title>App Python - {cfg['ambiente']}</title></head>
    <body style="background-color:{color}; font-family: sans-serif; color:white; text-align:center; padding-top:50px;">
        <h1 style="font-size:64px;">{cfg['ambiente'].upper()}</h1>
        <p>Rama: {cfg['rama']}</p>
        <p>Commit: {cfg['commit']}</p>
        <p>Versión: {cfg['version']}</p>
        <p>Implementacion: {cfg['esta app se instalo desde jenkins a minikube']}</p>

        <p>Stack: Python + Flask</p>
    </body>
    </html>
    """
    return html

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
