
"""
SecurePulse - Cloud-Based DevSecOps and Product Intelligence Platform
Entry point for the Flask application.
"""

import base64
import json
import os
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Flask, render_template, jsonify
from data.mock_data import get_dashboard_data

app = Flask(__name__)

# Docker Desktop can reach host services through host.docker.internal.
# Override JENKINS_URL with an environment variable if needed.
JENKINS_URL = os.environ.get(
    "JENKINS_URL", "http://host.docker.internal:8081"
).rstrip("/")
JENKINS_JOB = os.environ.get("JENKINS_JOB", "SecurePulse_CI-CD")


def get_jenkins_status():
    """Fetch the latest build details from Jenkins without exposing credentials."""
    api_url = (
        f"{JENKINS_URL}/job/{JENKINS_JOB}/lastBuild/api/json"
        "?tree=number,result,timestamp,url,building"
    )

    headers = {"Accept": "application/json"}
    username = os.environ.get("JENKINS_USER")
    token = os.environ.get("JENKINS_API_TOKEN")

    # Optional Jenkins API credentials, supplied through environment variables.
    if username and token:
        credentials = base64.b64encode(
            f"{username}:{token}".encode("utf-8")
        ).decode("ascii")
        headers["Authorization"] = f"Basic {credentials}"

    request = Request(api_url, headers=headers)

    try:
        with urlopen(request, timeout=4) as response:
            build = json.loads(response.read().decode("utf-8"))

        building = build.get("building", False)
        result = build.get("result")

        if building:
            status = "BUILDING"
        elif result:
            status = result
        else:
            status = "UNKNOWN"

        timestamp = build.get("timestamp")
        build_time = (
            datetime.fromtimestamp(timestamp / 1000).astimezone().isoformat(
                timespec="seconds"
            )
            if timestamp
            else None
        )

        return {
            "available": True,
            "status": status,
            "building": building,
            "build_number": build.get("number"),
            "build_time": build_time,
            "build_url": build.get("url"),
            # A successful pipeline means its configured stages passed.
            "security_gate": (
                "PASSED" if status == "SUCCESS"
                else "FAILED" if status == "FAILURE"
                else "PENDING"
            ),
            "message": "Latest Jenkins build retrieved."
        }

    except HTTPError as exc:
        message = (
            "Jenkins build not found."
            if exc.code == 404
            else f"Jenkins returned HTTP {exc.code}."
        )
    except (URLError, TimeoutError, OSError):
        message = "Jenkins is unreachable. Check its URL and availability."
    except (ValueError, KeyError):
        message = "Jenkins returned an invalid response."

    return {
        "available": False,
        "status": "UNAVAILABLE",
        "building": False,
        "build_number": None,
        "build_time": None,
        "build_url": None,
        "security_gate": "UNKNOWN",
        "message": message
    }


@app.route("/")
def index():
    """Render the main dashboard page."""
    return render_template("dashboard.html")


@app.route("/api/dashboard")
def dashboard_data():
    """Return the existing sample dashboard metrics."""
    return jsonify(get_dashboard_data())


@app.route("/api/jenkins-status")
def jenkins_status():
    """Return the latest Jenkins build status."""
    return jsonify(get_jenkins_status())


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", "5000"))
    print(f"Starting SecurePulse on http://{host}:{port} (debug={debug_mode})")
    app.run(host=host, port=port, debug=debug_mode)
