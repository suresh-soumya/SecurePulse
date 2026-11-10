# SecurePulse

**Cloud-Based DevSecOps and Product Intelligence Platform**

A college project built with Python (Flask), vanilla HTML/CSS/JavaScript, Docker, Jenkins, and Kubernetes.

SecurePulse provides a dashboard for monitoring application health, product metrics, DevOps performance, security vulnerabilities, and infrastructure status.

---

## Project Structure

```text
SecurePulse/
├── app.py
├── requirements.txt
├── README.md
├── Dockerfile
├── .dockerignore
├── .gitignore
├── Jenkinsfile
│
├── k8s/
│   ├── deployment.yaml       # Kubernetes Deployment
│   └── service.yaml          # Kubernetes NodePort Service
│
├── data/
│   ├── __init__.py
│   └── mock_data.py          # Sample metrics
│
├── templates/
│   └── dashboard.html        # Main dashboard page
│
├── static/
│   ├── css/
│   │   └── style.css         # Dashboard styling
│   └── js/
│       └── dashboard.js     # Dashboard data rendering
│
└── tests/
    ├── __init__.py
    └── test_app.py           # Pytest test suite
```

---

## Dashboard Sections

| Section | Cards |
|---|---|
| **Product Metrics** | Application Health, Active Users, Conversion Rate, Feature Usage |
| **DevOps Metrics** | Deployment Success Rate, Uptime, Response Time, Error Rate |
| **Security & Infrastructure** | Security Vulnerabilities, Infrastructure Status |

---

## Quick Start – Local Development

### 1. Clone or open the project

```bash
git clone YOUR_REPOSITORY_URL
cd SecurePulse
```

### 2. Create and activate a virtual environment

**Windows:**

```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

```bash
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

Open your browser:

http://127.0.0.1:5000

### 5. Run tests

```bash
pytest tests/ -v
```

---

## Docker – Stage 2

SecurePulse is containerized using Docker.

### Build the Docker image

```powershell
docker build -t securepulse:latest .
```

### Run the container

```powershell
docker run -d --name securepulse -p 5000:5000 securepulse:latest
```

Open:

http://localhost:5000

### View container logs

```powershell
docker logs securepulse
```

Stream live logs:

```powershell
docker logs -f securepulse
```

### Run tests inside the container

```powershell
docker run --rm securepulse:latest python -m pytest tests/ -v
```

---

## Jenkins CI/CD Pipeline – Stage 3

SecurePulse uses Jenkins for continuous integration and continuous delivery automation.

### Pipeline Workflow

```text
Checkout
   |
   v
Install Dependencies
   |
   v
Run Tests
   |
   v
Build Docker Image
```

### Pipeline Stages

| Stage | Description |
|---|---|
| **Checkout** | Jenkins fetches the latest source code from Git. |
| **Install Dependencies** | Installs Python dependencies in a dedicated virtual environment. |
| **Run Tests** | Executes automated tests using pytest and publishes JUnit test results. |
| **Build Docker Image** | Builds the SecurePulse Docker image after successful tests. |

### Agent Requirements

| Tool | Purpose |
|---|---|
| Python 3 | Runs the Flask application and tests |
| pip | Installs Python dependencies |
| Docker | Builds the application container |
| Git | Retrieves project source code |

### Jenkins Job Configuration

1. Open Jenkins.
2. Select **New Item**.
3. Create a Pipeline job.
4. Select **Pipeline script from SCM**.
5. Choose Git as the SCM.
6. Enter your repository URL.
7. Set Script Path to `Jenkinsfile`.
8. Save and select **Build Now**.

### Jenkins Integration

SecurePulse connects to Jenkins to retrieve pipeline build information.

The following environment variables are configured:

- `JENKINS_URL`
- `JENKINS_USER`
- `JENKINS_API_TOKEN`

Sensitive credentials are stored in a Kubernetes Secret named `jenkins-credentials`, rather than directly in the deployment manifest.

---

## Kubernetes Deployment – Stage 7

SecurePulse is deployed locally using Kubernetes through Minikube.

### Kubernetes Architecture

| Component | Configuration |
|---|---|
| Kubernetes Platform | Minikube |
| Container Image | `securepulse:latest` |
| Deployment | `securepulse` |
| Replicas | 1 |
| Container Port | 5000 |
| Service Type | NodePort |
| NodePort | 30843 |
| Kubernetes Secret | `jenkins-credentials` |

### Kubernetes Configuration Files

The `k8s/` directory contains:

```text
k8s/
├── deployment.yaml
└── service.yaml
```

**deployment.yaml**

Defines the SecurePulse Deployment, including:

- Application container configuration.
- Docker image and image pull policy.
- Container port.
- Jenkins environment variables.
- Kubernetes Secret references.

**service.yaml**

Defines the NodePort Service that exposes SecurePulse on port `30843`.

### Deployment Steps

#### 1. Start Minikube

```powershell
minikube start
```

#### 2. Load the Docker image into Minikube

```powershell
minikube image load securepulse:latest
```

#### 3. Apply the Kubernetes Deployment

```powershell
kubectl apply -f k8s/deployment.yaml
```

#### 4. Apply the Kubernetes Service

```powershell
kubectl apply -f k8s/service.yaml
```

#### 5. Verify Kubernetes resources

Check Deployment:

```powershell
kubectl get deployments
```

Check Pods:

```powershell
kubectl get pods
```

Check Services:

```powershell
kubectl get services
```

#### 6. Verify Deployment rollout

```powershell
kubectl rollout status deployment/securepulse
```

#### 7. Access SecurePulse

```powershell
minikube service securepulse
```

Minikube opens the application using the Service URL.

### Kubernetes Secret Management

Jenkins credentials are stored securely in Kubernetes:

```text
Secret Name: jenkins-credentials

Keys:
- JENKINS_API_TOKEN
- JENKINS_USER
```

The Deployment references these Secret keys using `secretKeyRef`.

This avoids hardcoding Jenkins credentials in the Kubernetes Deployment YAML file.

### Deployment Verification

The following have been verified in the local Minikube environment:

- SecurePulse Pod running successfully.
- Kubernetes Deployment available.
- NodePort Service configured.
- Jenkins integration operational.
- Jenkins dashboard retrieving build information.
- Security gate reporting PASSED.

---

## Roadmap

| Stage | Features | Status |
|---|---|---|
| Stage 1 | Flask application and dashboard | Completed |
| Stage 2 | Git and Docker containerization | Completed |
| Stage 3 | Jenkins CI/CD pipeline | Completed |
| Stage 4 | User authentication with Flask-Login | Planned |
| Stage 5 | AWS deployment (EC2 / ECS) | Planned |
| Stage 6 | Monitoring with Prometheus + Grafana | Planned |
| Stage 7 | Kubernetes orchestration with Minikube | Completed |

---

## Technologies Used

| Category | Technologies |
|---|---|
| Backend | Python 3.11+, Flask 3 |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Testing | pytest |
| Version Control | Git, GitHub |
| Containerization | Docker |
| CI/CD | Jenkins |
| Container Orchestration | Kubernetes |
| Local Kubernetes Environment | Minikube |
| Configuration | YAML |
| Secret Management | Kubernetes Secrets |

---

## Future Enhancements

- Implement user authentication and role-based access.
- Deploy SecurePulse to AWS.
- Integrate Prometheus and Grafana for monitoring.
- Implement automated vulnerability scanning.
- Improve CI/CD automation and deployment workflows.
- Explore Kubernetes deployment automation.

---

**SecurePulse – Cloud-Based DevSecOps and Product Intelligence Platform**

*College Project | 2026*
