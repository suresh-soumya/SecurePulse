/**
 * SecurePulse – Dashboard JavaScript
 * Fetches metrics from /api/dashboard and populates all cards.
 * Stage 1: Local Development
 */

"use strict";

// ── Helpers ────────────────────────────────────────────────────────────────

/** Set text content of an element by id (safe no-op if missing). */
function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

/** Set class names of an element by id. */
function setClass(id, ...classes) {
  const el = document.getElementById(id);
  if (el) el.className = classes.join(" ");
}

// ── Renderers ──────────────────────────────────────────────────────────────

function renderHealth(d) {
  const el = document.getElementById("health-status");
  if (el) {
    el.textContent = d.status;
    el.className = "metric-status status-" + d.status_class;
  }
  setText("health-details", d.details);
}

function renderUsers(d) {
  setText("users-value", d.value.toLocaleString());
  const el = document.getElementById("users-trend");
  if (el) {
    el.textContent = d.trend;
    el.className = "metric-trend trend-" + d.trend_class;
  }
}

function renderConversion(d) {
  setText("conversion-value", d.value + d.unit);
  const el = document.getElementById("conversion-trend");
  if (el) {
    el.textContent = d.trend;
    el.className = "metric-trend trend-" + d.trend_class;
  }
}

function renderFeatures(d) {
  const list = document.getElementById("feature-list");
  if (!list) return;
  list.innerHTML = d.top_features.map(f => `
    <li class="feature-item">
      <span class="feature-name">
        <span>${f.name}</span>
        <span>${f.usage}%</span>
      </span>
      <div class="feature-bar-track">
        <div class="feature-bar-fill" style="width: ${f.usage}%"></div>
      </div>
    </li>
  `).join("");
}

function renderDeploy(d) {
  setText("deploy-value", d.value + d.unit);
  setText("deploy-sub",
    `${d.total_deployments} total · ${d.failed_deployments} failed`);
}

function renderUptime(d) {
  setText("uptime-value", d.value + d.unit);
  setText("uptime-period", d.period);
}

function renderResponse(d) {
  setText("response-value", d.value + " " + d.unit);
  setText("response-sub", `Threshold: ${d.threshold} ms`);
}

function renderError(d) {
  setText("error-value", d.value + d.unit);
  const el = document.getElementById("error-trend");
  if (el) {
    el.textContent = d.trend;
    el.className = "metric-trend trend-" + d.trend_class;
  }
}

function renderSecurity(d) {
  setText("vuln-critical", d.critical);
  setText("vuln-high",     d.high);
  setText("vuln-medium",   d.medium);
  setText("vuln-low",      d.low);
  setText("vuln-scan",     "Last scan: " + d.last_scan);
}

function renderInfra(d) {
  const list = document.getElementById("infra-list");
  if (!list) return;
  list.innerHTML = d.services.map(s => `
    <li class="infra-item">
      <span class="infra-name">${s.name}</span>
      <span class="infra-badge badge-${s.status_class}">${s.status}</span>
    </li>
  `).join("");
}

// ── Main loader ────────────────────────────────────────────────────────────

async function loadDashboard() {
  try {
    const res = await fetch("/api/dashboard");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    setText("last-updated", "Updated: " + data.last_updated);

    renderHealth(data.application_health);
    renderUsers(data.active_users);
    renderConversion(data.conversion_rate);
    renderFeatures(data.feature_usage);
    renderDeploy(data.deployment_success_rate);
    renderUptime(data.uptime);
    renderResponse(data.response_time);
    renderError(data.error_rate);
    renderSecurity(data.security_vulnerabilities);
    renderInfra(data.infrastructure_status);

  } catch (err) {
    console.error("Failed to load dashboard data:", err);
    setText("last-updated", "Error loading data");
  }
}

// Load on page ready and auto-refresh every 30 seconds
document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();
  setInterval(loadDashboard, 30_000);
});
