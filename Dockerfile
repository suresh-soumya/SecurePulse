# ================================================================
# SecurePulse – Dockerfile
# Stage 2: Docker containerisation
# ================================================================

# ── Base image ────────────────────────────────────────────────────
# python:3.11-slim keeps the image small while matching the dev env.
FROM python:3.11-slim

# Apply available security updates to Debian base packages
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*
# ── Metadata ──────────────────────────────────────────────────────
LABEL maintainer="SecurePulse Project"
LABEL description="SecurePulse – Cloud-Based DevSecOps and Product Intelligence Platform"
LABEL stage="2-docker"

# ── Environment variables ─────────────────────────────────────────
# Prevents Python from writing .pyc files to disc.
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures Python output is sent straight to the terminal (no buffering).
ENV PYTHONUNBUFFERED=1
# Tell Flask to run in production mode inside the container.
ENV FLASK_ENV=production

# ── Working directory ─────────────────────────────────────────────
WORKDIR /app

# ── Install dependencies ──────────────────────────────────────────
# Copy requirements first so Docker layer-caches the install step.
# The local venv is excluded via .dockerignore.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application source ───────────────────────────────────────
COPY . .

# ── Expose port ───────────────────────────────────────────────────
EXPOSE 5000

# ── Run the application ───────────────────────────────────────────
# Gunicorn is not added yet to keep Stage 2 minimal.
# Flask''s built-in server listens on 0.0.0.0 so the container port
# is reachable from the host via -p 5000:5000.
CMD ["python", "app.py"]
