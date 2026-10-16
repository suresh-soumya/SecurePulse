"""
Basic tests for the SecurePulse Flask application.
Run with: pytest tests/
"""

import pytest
import sys
import os

# Allow imports from the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from data.mock_data import get_dashboard_data


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """Create a Flask test client with testing mode enabled."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── Route tests ────────────────────────────────────────────────────────────

def test_dashboard_page_loads(client):
    """GET / should return HTTP 200 and the dashboard HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"SecurePulse" in response.data


def test_api_dashboard_returns_json(client):
    """GET /api/dashboard should return HTTP 200 with valid JSON."""
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_api_dashboard_has_required_keys(client):
    """The JSON response must contain all expected top-level keys."""
    response = client.get("/api/dashboard")
    data = response.get_json()
    required_keys = [
        "last_updated",
        "application_health",
        "active_users",
        "conversion_rate",
        "feature_usage",
        "deployment_success_rate",
        "uptime",
        "response_time",
        "error_rate",
        "security_vulnerabilities",
        "infrastructure_status",
    ]
    for key in required_keys:
        assert key in data, f"Missing key in API response: {key}"


# ── Mock data tests ────────────────────────────────────────────────────────

def test_mock_data_active_users_in_range():
    """Active users should be a positive integer."""
    data = get_dashboard_data()
    users = data["active_users"]["value"]
    assert isinstance(users, int)
    assert users > 0


def test_mock_data_uptime_high():
    """Uptime should be above 99% to reflect a healthy system."""
    data = get_dashboard_data()
    uptime = data["uptime"]["value"]
    assert uptime >= 99.0, f"Uptime unexpectedly low: {uptime}"


def test_mock_data_feature_usage_has_items():
    """Feature usage list should contain at least one feature."""
    data = get_dashboard_data()
    features = data["feature_usage"]["top_features"]
    assert len(features) > 0


def test_mock_data_infra_services_present():
    """Infrastructure status must list at least one service."""
    data = get_dashboard_data()
    services = data["infrastructure_status"]["services"]
    assert len(services) > 0
    for svc in services:
        assert "name" in svc
        assert "status" in svc
