/*
 * SecurePulse – Declarative Jenkins Pipeline
 * Stage 3: CI/CD with Jenkins
 *
 * Agent requirements
 * ------------------
 *   • Python 3    (python3 / python both tried; see Install Dependencies stage)
 *   • pip         (bundled with Python 3.4+)
 *   • Docker      (daemon must be running; Jenkins user needs docker group access)
 *   • pip-audit   (installed into the build venv during Security Scan stage)
 *   • Trivy       (downloaded to .trivy-bin/ in the workspace if not on PATH;
 *                  no changes to the Jenkins container or host)
 *
 * No credentials or secrets are hardcoded.
 * The Docker image is built locally only – no push to any registry.
 *
 * Security Scan blocking policy
 * ------------------------------
 *   pip-audit : any vulnerability → pipeline fails
 *   Trivy     : HIGH or CRITICAL severity in the image → pipeline fails
 *               (informational LOW/MEDIUM findings are printed but non-blocking)
 */

pipeline {

    // ── Agent ──────────────────────────────────────────────────────────────
    // 'any' lets Jenkins pick whichever agent has Python + Docker installed.
    // Replace with agent { label 'python-docker' } if you tag a specific node.
    agent any

    // ── Environment ────────────────────────────────────────────────────────
    environment {
        IMAGE_NAME  = "securepulse"
        IMAGE_TAG   = "latest"
        VENV_DIR    = ".jenkins-venv"   // isolated venv – never committed to Git
    }

    // ── Options ────────────────────────────────────────────────────────────
    options {
        // Discard old builds: keep last 10 logs, last 3 artifacts
        buildDiscarder(logRotator(numToKeepStr: "10", artifactNumToKeepStr: "3"))
        // Fail the build if it hangs for more than 20 minutes
        timeout(time: 20, unit: "MINUTES")
        // Prevent two builds of the same branch running at once
        disableConcurrentBuilds()
        timestamps()
    }

    // ── Stages ─────────────────────────────────────────────────────────────
    stages {

        // ── 1. Checkout ────────────────────────────────────────────────────
        stage("Checkout") {
            steps {
                echo "==> Checking out source code..."
                // Declarative pipelines check out the SCM automatically when
                // configured via a Multibranch Pipeline or Pipeline from SCM job.
                // The explicit checkout step below is a safe no-op in that case
                // but makes the Jenkinsfile self-contained for manual runs.
                checkout scm
                echo "Workspace: ${env.WORKSPACE}"
                sh "ls -la"
            }
        }

        // ── 2. Install Dependencies ────────────────────────────────────────
        stage("Install Dependencies") {
            steps {
                echo "==> Creating virtual environment and installing dependencies..."
                sh """
                    # Use python3 if available, fall back to python
                    PYTHON=\$(command -v python3 || command -v python)
                    echo "Using Python: \$PYTHON"
                    \$PYTHON --version

                    # Create a fresh isolated venv for this build
                    \$PYTHON -m venv ${VENV_DIR}

                    # Install all requirements (Flask + pytest)
                    ${VENV_DIR}/bin/pip install --upgrade pip --quiet
                    ${VENV_DIR}/bin/pip install -r requirements.txt --quiet

                    echo "Installed packages:"
                    ${VENV_DIR}/bin/pip list
                """
            }
        }

        // ── 3. Run Tests ───────────────────────────────────────────────────
        stage("Run Tests") {
            steps {
                echo "==> Running pytest suite..."
                sh """
                    ${VENV_DIR}/bin/python -m pytest tests/ -v \
                        --tb=short \
                        --junit-xml=test-results.xml
                """
            }
            post {
                always {
                    // Publish JUnit test results in the Jenkins UI
                    junit allowEmptyResults: true, testResults: "test-results.xml"
                }
                failure {
                    echo "Tests FAILED – Docker build will be skipped."
                }
                success {
                    echo "All tests PASSED."
                }
            }
        }

        // ── 4. Build Docker Image ──────────────────────────────────────────
        // This stage only runs when the Run Tests stage succeeds.
        stage("Build Docker Image") {
            steps {
                echo "==> Building Docker image ${IMAGE_NAME}:${IMAGE_TAG}..."
                sh """
                    docker build \
                        --no-cache \
                        -t ${IMAGE_NAME}:${IMAGE_TAG} \
                        -t ${IMAGE_NAME}:build-${env.BUILD_NUMBER} \
                        .
                    echo "Docker image built successfully:"
                    docker images ${IMAGE_NAME}
                """
            }
            post {
                success {
                    echo "Image ${IMAGE_NAME}:${IMAGE_TAG} is ready. Push to a registry manually when required."
                }
            }
        }

        // ── 5. Security Scan ───────────────────────────────────────────────
        // Runs AFTER the image is built so Trivy can scan the real image.
        // Both sub-scans must pass before deployment is allowed.
        stage("Security Scan") {
            steps {
                echo "==> Running security scans..."
                sh """
                    # ── pip-audit: dependency vulnerability scan ───────────────────────
                    echo "--- [1/2] pip-audit: scanning requirements.txt ---"

                    # pip-audit is installed into the existing build venv so we never
                    # touch the Jenkins container or any system-level package manager.
                    ${VENV_DIR}/bin/pip install pip-audit --quiet

                    # Scan requirements.txt directly (fastest, no env resolution needed).
                    # Any vulnerability causes a non-zero exit → stage fails immediately.
                    ${VENV_DIR}/bin/pip-audit -r requirements.txt --progress-spinner off
                    echo "pip-audit: PASSED – no known vulnerabilities in requirements.txt"

                    # ── Trivy: container image vulnerability scan ──────────────────────
                    echo "--- [2/2] Trivy: scanning ${IMAGE_NAME}:${IMAGE_TAG} ---"

                    # Prefer a system-installed trivy; fall back to a workspace-local
                    # binary so the Jenkins container itself is never modified.
                    TRIVY_BIN=\$(command -v trivy 2>/dev/null || echo "")

                    if [ -z "\$TRIVY_BIN" ]; then
                        echo "trivy not found on PATH – downloading to .trivy-bin/ ..."
                        mkdir -p .trivy-bin

                        # Fetch the latest stable version tag from GitHub API
                        TRIVY_VERSION=\$(curl -sSfL \
                            "https://api.github.com/repos/aquasecurity/trivy/releases/latest" \
                            | grep '"tag_name"' \
                            | sed 's/.*"v\\([^"]*\\)".*/\\1/')
                        # Guard: fail clearly if the version string could not be resolved
                        if [ -z "\${TRIVY_VERSION}" ]; then
                            echo "ERROR: Could not resolve latest Trivy version from GitHub API."
                            echo "       Check network access and that the API response contains 'tag_name'."
                            exit 1
                        fi
                        echo "Downloading Trivy v\${TRIVY_VERSION}..."

                        curl -sSfL \
                            --retry 5 \
                            --retry-all-errors \
                            --retry-delay 2 \
                            --connect-timeout 20 \
                            --max-time 300 \
                            "https://github.com/aquasecurity/trivy/releases/download/v\${TRIVY_VERSION}/trivy_\${TRIVY_VERSION}_Linux-64bit.tar.gz" \
                            -o .trivy-bin/trivy.tar.gz
                        tar -xzf .trivy-bin/trivy.tar.gz -C .trivy-bin trivy
                        chmod +x .trivy-bin/trivy
                        TRIVY_BIN=".trivy-bin/trivy"
                        echo "Trivy downloaded: \$(\$TRIVY_BIN --version)"
                    else
                        echo "Using system Trivy: \$(\$TRIVY_BIN --version)"
                    fi

                    # Cache the vulnerability DB inside the workspace (not the container).
                    export TRIVY_CACHE_DIR="\${WORKSPACE}/.trivy-cache"
                    mkdir -p "\${TRIVY_CACHE_DIR}"

                    # Scan the locally built image.
                    # --exit-code 1  → non-zero exit when HIGH or CRITICAL are found.
                    # --severity     → only block on HIGH and CRITICAL.
                    # --no-progress  → cleaner Jenkins log output.
                    # The full table (including LOW/MEDIUM) is always printed first.
                    echo "Trivy informational scan (all severities):"
                    \$TRIVY_BIN image \
                        --cache-dir "\${TRIVY_CACHE_DIR}" \
                        --no-progress \
                        --exit-code 0 \
                        --severity LOW,MEDIUM,HIGH,CRITICAL \
                        ${IMAGE_NAME}:${IMAGE_TAG}

                    echo "Trivy blocking scan (HIGH + CRITICAL only):"
                    \$TRIVY_BIN image \
                        --cache-dir "\${TRIVY_CACHE_DIR}" \
                        --no-progress \
                        --exit-code 1 \
                        --severity HIGH,CRITICAL \
                        ${IMAGE_NAME}:${IMAGE_TAG}

                    echo "Trivy: PASSED – no HIGH or CRITICAL vulnerabilities found in ${IMAGE_NAME}:${IMAGE_TAG}"
                """
            }
            post {
                success {
                    echo "Security Scan PASSED – pip-audit and Trivy found no blocking vulnerabilities."
                }
                failure {
                    echo "Security Scan FAILED – vulnerabilities detected. Deployment is blocked. Review scan output above."
                }
                always {
                    // Clean up the downloaded Trivy binary to keep the workspace tidy.
                    // The DB cache (.trivy-cache/) is intentionally kept to speed up
                    // subsequent builds (Trivy will only download deltas).
                    sh "rm -f .trivy-bin/trivy .trivy-bin/trivy.tar.gz || true"
                }
            }
        }

        // ── 6. Deploy SecurePulse ──────────────────────────────────────────
        // Replaces only the securepulse-app container; all other containers
        // (e.g. PCARP) are left completely untouched.
        stage("Deploy SecurePulse") {
            steps {
                echo "==> Deploying ${IMAGE_NAME}:${IMAGE_TAG} as securepulse-app..."
                sh """
                    # ── Stop & remove the existing securepulse-app container (if any) ──
                    # We scope the filter to the exact container name so that no other
                    # container (PCARP or otherwise) is ever touched.
                    if docker ps -a --filter "name=^securepulse-app\$" --format '{{.Names}}' | grep -q '^securepulse-app\$'; then
                        echo "Stopping existing securepulse-app container..."
                        docker stop securepulse-app
                        echo "Removing existing securepulse-app container..."
                        docker rm   securepulse-app
                    else
                        echo "No existing securepulse-app container found – fresh deploy."
                    fi

                    # ── Start the newly built image ────────────────────────────────────
                    docker run -d \
                        --name securepulse-app \
                        --restart unless-stopped \
                        -p 5001:5000 \
                        ${IMAGE_NAME}:${IMAGE_TAG}

                    echo "Container started. Waiting 5 s for the app to initialise..."
                    sleep 5

                    # ── Verify the container is actually running ────────────────────────
                    STATUS=\$(docker inspect -f '{{.State.Status}}' securepulse-app 2>/dev/null || echo "not_found")
                    echo "Container status: \${STATUS}"

                    if [ "\${STATUS}" != "running" ]; then
                        echo "ERROR: securepulse-app is NOT running (status=\${STATUS})."
                        echo "Container logs:"
                        docker logs securepulse-app || true
                        exit 1
                    fi

                    echo "Deployment VERIFIED – securepulse-app is running on host port 5001."
                    docker ps --filter "name=^securepulse-app\$"
                """
            }
            post {
                success {
                    echo "Deploy stage PASSED – securepulse-app is live on port 5001."
                }
                failure {
                    echo "Deploy stage FAILED – securepulse-app did not start correctly. Review logs above."
                }
            }
        }

    }   // end stages

    // ── Post (global) ──────────────────────────────────────────────────────
    post {
        always {
            echo "==> Cleaning up virtual environment..."
            sh "rm -rf ${VENV_DIR}"
            echo "Pipeline finished. Status: ${currentBuild.currentResult}"
        }
        success {
            echo "BUILD SUCCEEDED – SecurePulse image is ready."
        }
        failure {
            echo "BUILD FAILED – review the stage logs above."
        }
        unstable {
            echo "BUILD UNSTABLE – some tests may have been skipped or flaky."
        }
    }

}
