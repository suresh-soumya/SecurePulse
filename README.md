# SecurePulse

**Cloud-Based DevSecOps and Product Intelligence Platform**

A college project built with Python (Flask) and vanilla HTML/CSS/JS.  
Stage 3 – CI/CD with Jenkins.

---

## Project Structure

```
SecurePulse/
├── app.py                  # Flask entry point
├── requirements.txt        # Python dependencies
├── README.md
├── Dockerfile              # Container image definition  [Stage 2]
├── .dockerignore           # Files excluded from Docker build context  [Stage 2]
├── .gitignore              # Files excluded from Git  [Stage 2]
├── Jenkinsfile             # Declarative CI/CD pipeline  [Stage 3]
│
├── data/
│   ├── __init__.py
│   └── mock_data.py        # Sample metrics (replace with real data later)
│
├── templates/
│   └── dashboard.html      # Main dashboard page (Jinja2 template)
│
├── static/
│   ├── css/
│   │   └── style.css       # Dark-theme dashboard styles
│   └── js/
│       └── dashboard.js    # Fetches /api/dashboard and renders cards
│
└── tests/
    ├── __init__.py
    └── test_app.py         # Pytest test suite
```

---

## Dashboard Sections

| Section | Cards |
|---|---|
| **Product Metrics** | Application Health, Active Users, Conversion Rate, Feature Usage |
| **DevOps Metrics** | Deployment Success Rate, Uptime, Response Time, Error Rate |
| **Security & Infrastructure** | Security Vulnerabilities, Infrastructure Status |

---

## Quick Start

### 1. Clone / open the project

```bash
cd SecurePulse
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

Open your browser at **http://127.0.0.1:5000**

### 5. Run the tests

```bash
pytest tests/ -v
```

---

## Docker (Stage 2)

### Build the image

```powershell
docker build -t securepulse:latest .
```

### Run the container

```powershell
docker run -d --name securepulse -p 5000:5000 securepulse:latest
```

Open your browser at **http://localhost:5000**

### View container logs

```powershell
docker logs securepulse

# Stream live logs:
docker logs -f securepulse
```

### Stop and remove the container

```powershell
docker stop securepulse
docker rm securepulse
```

### Run tests inside the container (one-off, then remove)

```powershell
docker run --rm securepulse:latest python -m pytest tests/ -v
```

---

## Jenkins CI/CD Pipeline (Stage 3)

### How the pipeline works

The `Jenkinsfile` defines a **Declarative Pipeline** with four sequential stages:

```
Checkout  →  Install Dependencies  →  Run Tests  →  Build Docker Image
```

| Stage | What happens |
|---|---|
| **Checkout** | Jenkins fetches the latest source code from your SCM (Git). |
| **Install Dependencies** | A fresh Python virtual environment (`.jenkins-venv`) is created on the agent. `pip` installs `Flask` and `pytest` from `requirements.txt`. The local `venv/` folder is never used or copied. |
| **Run Tests** | Runs `python -m pytest tests/ -v --junit-xml=test-results.xml`. Results are published in the Jenkins UI via the JUnit plugin. The build is marked **FAILED** if any test fails and the Docker build stage is skipped. |
| **Build Docker Image** | **Only runs if all tests pass.** Builds `securepulse:latest` and tags it with the build number (e.g. `securepulse:build-42`) for traceability. No image is pushed to any registry. |

### Agent requirements

The Jenkins agent (node) must have the following installed:

| Tool | Notes |
|---|---|
| **Python 3** | `python3` or `python` must be on `PATH`. Any 3.x version works. |
| **pip** | Bundled with Python 3.4+; used inside the per-build venv only. |
| **Docker** | Daemon must be running; the `jenkins` OS user must belong to the `docker` group: `sudo usermod -aG docker jenkins && sudo systemctl restart jenkins` |

### Setting up the Jenkins job

1. **Install plugins** (Manage Jenkins → Plugin Manager):
   - *Pipeline* (usually pre-installed)
   - *JUnit* (for test result graphs)
   - *Git* (for SCM checkout)

2. **Create a new job:**
   - New Item → **Pipeline** (or **Multibranch Pipeline** for branch-per-PR workflows)
   - Pipeline → Definition: **Pipeline script from SCM**
   - SCM: **Git** → Repository URL: your repo URL
   - Script Path: `Jenkinsfile`
   - Save → **Build Now**

3. **View results:**
   - Stage view shows each stage's pass/fail in colour.
   - *Test Result Trend* graph appears after the first run.
   - Console Output contains the full `pytest -v` log.

---

## Roadmap

| Stage | Features |
|---|---|
| ✅ **Stage 1** | Local Flask app, mock data, basic dashboard |
| ✅ **Stage 2** | Git (`.gitignore`) + Docker (`Dockerfile`, `.dockerignore`) |
| ✅ **Stage 3** | CI/CD with Jenkins (`Jenkinsfile` – declarative pipeline) |
| 🔜 Stage 4 | User authentication (Flask-Login) |
| 🔜 Stage 5 | AWS deployment (EC2 / ECS) |
| 🔜 Stage 6 | Monitoring with Prometheus + Grafana |
| 🔜 Stage 7 | Kubernetes orchestration |

---

## Technologies

- **Backend** – Python 3.11+, Flask 3
- **Frontend** – HTML5, CSS3, Vanilla JavaScript (ES2020)
- **Testing** – pytest
- **Containerisation** – Docker
- **CI/CD** – Jenkins (Declarative Pipeline)

---

*SecurePulse – College Project, 2026*
