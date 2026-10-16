# SecurePulse

**Cloud-Based DevSecOps and Product Intelligence Platform**

A college project built with Python (Flask) and vanilla HTML/CSS/JS.  
Stage 2 – Git & Docker containerisation.

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

## Roadmap

| Stage | Features |
|---|---|
| ✅ **Stage 1** | Local Flask app, mock data, basic dashboard |
| ✅ **Stage 2** | Git (`.gitignore`) + Docker (`Dockerfile`, `.dockerignore`) |
| 🔜 Stage 3 | User authentication (Flask-Login) |
| 🔜 Stage 4 | CI/CD with Jenkins / GitHub Actions |
| 🔜 Stage 5 | AWS deployment (EC2 / ECS) |
| 🔜 Stage 6 | Monitoring with Prometheus + Grafana |
| 🔜 Stage 7 | Kubernetes orchestration |

---

## Technologies

- **Backend** – Python 3.11+, Flask 3
- **Frontend** – HTML5, CSS3, Vanilla JavaScript (ES2020)
- **Testing** – pytest
- **Containerisation** – Docker

---

*SecurePulse – College Project, 2026*

