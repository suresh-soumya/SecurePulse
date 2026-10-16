"""
Mock data module for SecurePulse dashboard.
Provides realistic sample metrics for all dashboard cards.
In future stages, replace these with real API/database calls.
"""

import random
from datetime import datetime


def get_dashboard_data():
    """
    Return a dictionary of mock metrics for the dashboard.
    Slight randomisation simulates live-ish data on each page refresh.
    """
    return {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        # -- Product metrics -----------------------------------------
        "application_health": {
            "status": "Healthy",
            "status_class": "success",
            "details": "All systems operational"
        },
        "active_users": {
            "value": random.randint(1_180, 1_320),
            "trend": "+12% vs last week",
            "trend_class": "up"
        },
        "conversion_rate": {
            "value": round(random.uniform(3.2, 4.1), 1),
            "unit": "%",
            "trend": "+0.3% vs last month",
            "trend_class": "up"
        },
        "feature_usage": {
            "top_features": [
                {"name": "Dashboard Analytics", "usage": random.randint(78, 92)},
                {"name": "Security Scanner",    "usage": random.randint(61, 75)},
                {"name": "Deploy Tracker",      "usage": random.randint(44, 58)},
                {"name": "Alerting Engine",     "usage": random.randint(30, 44)},
            ]
        },

        # -- DevOps metrics -------------------------------------------
        "deployment_success_rate": {
            "value": round(random.uniform(94.0, 99.5), 1),
            "unit": "%",
            "total_deployments": random.randint(38, 55),
            "failed_deployments": random.randint(1, 3)
        },
        "uptime": {
            "value": round(random.uniform(99.70, 99.99), 2),
            "unit": "%",
            "period": "Last 30 days"
        },
        "response_time": {
            "value": random.randint(95, 145),
            "unit": "ms",
            "threshold": 200,
            "status_class": "success"
        },
        "error_rate": {
            "value": round(random.uniform(0.05, 0.45), 2),
            "unit": "%",
            "trend": "-0.1% vs yesterday",
            "trend_class": "down-good"
        },

        # -- Security metrics -----------------------------------------
        "security_vulnerabilities": {
            "critical": random.randint(0, 1),
            "high":     random.randint(2, 5),
            "medium":   random.randint(5, 12),
            "low":      random.randint(10, 20),
            "last_scan": "2026-09-04 12:00 IST"
        },

        # -- Infrastructure metrics -----------------------------------
        "infrastructure_status": {
            "services": [
                {"name": "Web Server",   "status": "Online",  "status_class": "success"},
                {"name": "Database",     "status": "Online",  "status_class": "success"},
                {"name": "Cache Layer",  "status": "Online",  "status_class": "success"},
                {"name": "Message Queue","status": "Degraded","status_class": "warning"},
                {"name": "CDN",          "status": "Online",  "status_class": "success"},
            ]
        }
    }
