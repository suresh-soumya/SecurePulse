# ================================================================
# SecurePulse – Dockerfile
# Stage 2: Docker containerisation
# ================================================================

# ── Stage 1: Build dependencies ───────────────────────────────────
FROM python:3.11-slim-trixie AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build

# Upgrade installation tools and security-sensitive dependencies
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir --upgrade "urllib3>=2.8.0" "msgpack>=1.2.1" "jaraco.context>=6.1.0"

# Install only the runtime dependency into a separate directory
RUN python -m pip install --no-cache-dir --prefix=/install "Flask==3.1.3" "boto3==1.43.127"


# ── Stage 2: Production image ─────────────────────────────────────
FROM python:3.11-slim-trixie

# Apply available security updates to Debian base packages
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*
# ── Metadata ──────────────────────────────────────────────────────
LABEL maintainer="SecurePulse Project"
LABEL description="SecurePulse – Cloud-Based DevSecOps and Product Intelligence Platform"
LABEL stage="2-docker"

# ── Environment variables ─────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# ── Working directory ─────────────────────────────────────────────
WORKDIR /app

# Copy installed Flask runtime dependencies from the builder
COPY --from=builder /install /usr/local

# Remove build tooling not needed by the Flask runtime
RUN python -m pip uninstall -y setuptools

# Copy application source
COPY . .

# ── Expose application port ───────────────────────────────────────
EXPOSE 5000

# ── Start SecurePulse ─────────────────────────────────────────────
CMD ["python", "app.py"]