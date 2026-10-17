
/*
 * SecurePulse – Declarative Jenkins Pipeline
 * Stage 3: CI/CD with Jenkins
 *
 * Agent requirements
 * ------------------
 *   • Python 3   (python3 / python both tried; see Install Dependencies stage)
 *   • pip        (bundled with Python 3.4+)
 *   • Docker     (daemon must be running; Jenkins user needs Docker socket access)
 *   • pip-audit  (installed into the build venv during Security Scan stage)
 *   • Trivy      (runs from the official aquasec/trivy Docker image)
 *
 * No credentials or secrets are hardcoded.
 * The Docker image is built locally only – no push to any registry.
 *
 * Security Scan blocking policy
 * -----------------------------
 *   pip-audit : any known dependency vulnerability fails the pipeline
 *   Trivy     : HIGH or CRITICAL image vulnerabilities fail the pipeline
 *               Informational scan reports all severities.
 */

pipeline {

    // Agent
    agent any

    // Environment
    environment {
        IMAGE_NAME = "securepulse"
        IMAGE_TAG  = "latest"
        VENV_DIR   = ".jenkins-venv"
    }

    // Options
    options {
        buildDiscarder(logRotator(numToKeepStr: "10", artifactNumToKeepStr: "3"))
        timeout(time: 20, unit: "MINUTES")
        disableConcurrentBuilds()
        timestamps()
    }

    // Stages
    stages {

        stage("Checkout") {
            steps {
                echo "==> Checking out source code..."
                checkout scm
                echo "Workspace: ${env.WORKSPACE}"
                sh "ls -la"
            }
        }

        stage("Install Dependencies") {
            steps {
                echo "==> Creating virtual environment and installing dependencies..."
                sh """
                    PYTHON=\$(command -v python3 || command -v python)
                    echo "Using Python: \$PYTHON"
                    \$PYTHON --version

                    \$PYTHON -m venv ${VENV_DIR}
                    ${VENV_DIR}/bin/pip install --upgrade pip --quiet
                    ${VENV_DIR}/bin/pip install -r requirements.txt --quiet

                    echo "Installed packages:"
                    ${VENV_DIR}/bin/pip list
                """
            }
        }

        stage("Run Tests") {
            steps {
                echo "==> Running pytest suite..."
                sh """
                    ${VENV_DIR}/bin/python -m pytest tests/ -v \\
                        --tb=short \\
                        --junit-xml=test-results.xml
                """
            }
            post {
                always {
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

        stage("Build Docker Image") {
            steps {
                echo "==> Building Docker image ${IMAGE_NAME}:${IMAGE_TAG}..."
                sh """
                    docker build \\
                        --no-cache \\
                        -t ${IMAGE_NAME}:${IMAGE_TAG} \\
                        -t ${IMAGE_NAME}:build-${env.BUILD_NUMBER} \\
                        .
                    echo "Docker image built successfully:"
                    docker images ${IMAGE_NAME}
                """
            }
            post {
                success {
                    echo "Image ${IMAGE_NAME}:${IMAGE_TAG} is ready for scanning."
                }
            }
        }

        stage("Security Scan") {
            steps {
                echo "==> Running security scans..."
                sh """
                    set -eu

                    # pip-audit: scan pinned Python dependencies.
                    echo "--- [1/2] pip-audit: scanning requirements.txt ---"
                    ${VENV_DIR}/bin/pip install pip-audit --quiet
                    ${VENV_DIR}/bin/pip-audit -r requirements.txt --progress-spinner off
                    echo "pip-audit: PASSED – no known vulnerabilities in requirements.txt"

                    # Trivy: use its official Docker image instead of downloading a binary.
                    echo "--- [2/2] Trivy: scanning ${IMAGE_NAME}:${IMAGE_TAG} ---"
                    docker pull aquasec/trivy:0.76.0
                    docker volume create securepulse-trivy-cache >/dev/null

                    # Export the just-built image to the Jenkins workspace. The trap
                    # removes the archive even if a scan fails.
                    ARCHIVE_PATH="\${WORKSPACE}/.securepulse-image.tar"
                    trap 'rm -f "\$ARCHIVE_PATH"' EXIT
                    docker save --output "\$ARCHIVE_PATH" ${IMAGE_NAME}:${IMAGE_TAG}

                    # The archive is exposed read-only to Trivy from the existing
                    # Jenkins home volume. The scanner cannot modify the workspace.
                    echo "Trivy informational scan (all severities):"
                    docker run --rm \\
                        --mount type=volume,src=jenkins_home,dst=/workspace,readonly,volume-subpath=workspace/SecurePulse_CI-CD \\
                        --mount type=volume,src=securepulse-trivy-cache,dst=/root/.cache/trivy \\
                        aquasec/trivy:0.76.0 image \\
                        --cache-dir /root/.cache/trivy \\
                        --input /workspace/.securepulse-image.tar \\
                        --no-progress \\
                        --exit-code 0 \\
                        --severity UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL

                    echo "Trivy blocking scan (HIGH + CRITICAL only):"
                    docker run --rm \\
                        --mount type=volume,src=jenkins_home,dst=/workspace,readonly,volume-subpath=workspace/SecurePulse_CI-CD \\
                        --mount type=volume,src=securepulse-trivy-cache,dst=/root/.cache/trivy \\
                        aquasec/trivy:0.76.0 image \\
                        --cache-dir /root/.cache/trivy \\
                        --input /workspace/.securepulse-image.tar \\
                        --no-progress \\
                        --exit-code 1 \\
                        --severity HIGH,CRITICAL

                    echo "Trivy: PASSED – no HIGH or CRITICAL vulnerabilities found in ${IMAGE_NAME}:${IMAGE_TAG}"
                """
            }
            post {
                success {
                    echo "Security Scan PASSED – pip-audit and Trivy found no blocking vulnerabilities."
                }
                failure {
                    echo "Security Scan FAILED – vulnerabilities or scanner errors detected. Deployment is blocked. Review scan output above."
                }
            }
        }

        stage("Deploy SecurePulse") {
            steps {
                echo "==> Deploying ${IMAGE_NAME}:${IMAGE_TAG} as securepulse-app..."
                sh """
                    set -eu

                    # Select only the exact securepulse-app container name.
                    if docker ps -a --filter "name=^securepulse-app\$" --format '{{.Names}}' | grep -q '^securepulse-app\$'; then
                        echo "Stopping existing securepulse-app container..."
                        docker stop securepulse-app
                        echo "Removing existing securepulse-app container..."
                        docker rm securepulse-app
                    else
                        echo "No existing securepulse-app container found – fresh deploy."
                    fi

                    docker run -d \\
                        --name securepulse-app \\
                        --restart unless-stopped \\
                        -p 5001:5000 \\
                        ${IMAGE_NAME}:${IMAGE_TAG}

                    echo "Container started. Waiting 5 seconds for the app to initialize..."
                    sleep 5

                    STATUS=\$(docker inspect -f '{{.State.Status}}' securepulse-app 2>/dev/null || echo "not_found")
                    echo "Container status: \$STATUS"
                    if [ "\$STATUS" != "running" ]; then
                        echo "ERROR: securepulse-app is NOT running (status=\$STATUS)."
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
    }

    post {
        always {
            echo "==> Cleaning up virtual environment..."
            sh "rm -rf ${VENV_DIR}"
            echo "Pipeline finished. Status: ${currentBuild.currentResult}"
        }
        success {
            echo "BUILD SUCCEEDED – SecurePulse tests, image build, security scans, and deployment completed."
        }
        failure {
            echo "BUILD FAILED – review the stage logs above."
        }
        unstable {
            echo "BUILD UNSTABLE – some tests may have been skipped or flaky."
        }
    }
}
