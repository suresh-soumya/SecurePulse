"""
SecurePulse - Cloud-Based DevSecOps and Product Intelligence Platform
Entry point for the Flask application.
"""

from flask import Flask, render_template, jsonify
from data.mock_data import get_dashboard_data

app = Flask(__name__)


@app.route("/")
def index():
    """Render the main dashboard page."""
    return render_template("dashboard.html")


@app.route("/api/dashboard")
def dashboard_data():
    """
    API endpoint that returns mock dashboard metrics as JSON.
    In future stages, this will pull from real data sources.
    """
    data = get_dashboard_data()
    return jsonify(data)


if __name__ == "__main__":
    import os
    # FLASK_DEBUG=1 enables debug mode locally; leave unset (or 0) in Docker/production.
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", "5000"))
    print(f"Starting SecurePulse on http://{host}:{port}  (debug={debug_mode})")
    app.run(host=host, port=port, debug=debug_mode)
