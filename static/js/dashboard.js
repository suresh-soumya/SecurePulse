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

/**
 * Load the latest Jenkins CI/CD build status.
 */
async function loadJenkinsStatus() {
  try {
    const response = await fetch("/api/jenkins-status", {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    setText("jenkins-status", data.status || "UNKNOWN");
    setText(
      "jenkins-build",
      "Latest build: " +
        (data.build_number == null ? "--" : "#" + data.build_number)
    );
    setText("jenkins-gate", "Security gate: " + data.security_gate);
    setText(
      "jenkins-time",
      "Build time: " + (data.build_time || "Not available")
    );
    setText("jenkins-message", data.message || "");

    const statusElement = document.getElementById("jenkins-status");
    if (statusElement) {
      statusElement.className = "metric-status";

      if (data.status === "SUCCESS") {
        statusElement.classList.add("status-healthy");
      } else if (
        data.status === "FAILURE" ||
        data.status === "UNSTABLE"
      ) {
        statusElement.classList.add("status-unhealthy");
      }
    }

    const link = document.getElementById("jenkins-link");
    if (link) {
      const buildUrl = data.build_url
        ? new URL(data.build_url)
        : null;

      if (
        data.available &&
        buildUrl &&
        buildUrl.origin === "http://localhost:8081"
      ) {
        link.href = buildUrl.href;
        link.hidden = false;
      } else {
        link.hidden = true;
      }
    }
  } catch (error) {
    console.error("Failed to load Jenkins status:", error);
    setText("jenkins-status", "UNAVAILABLE");
    setText("jenkins-gate", "Security gate: UNKNOWN");
    setText("jenkins-message", "Could not retrieve Jenkins status.");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();
  loadJenkinsStatus();

  setInterval(loadDashboard, 30_000);
  setInterval(loadJenkinsStatus, 30_000);
});
