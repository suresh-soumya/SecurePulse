/*
 * SecurePulse - Declarative Jenkins Pipeline
 * Stage 3: CI/CD with Jenkins
 *
 * Agent requirements
 * ------------------
 *   - Python 3 (python3 or python)
 *   - pip
 *   - Docker (daemon running; Jenkins user can access Docker socket)
 *   - Trivy runs from the official aquasec/trivy Docker image
 *
 * No credentials or secrets are hardcoded.
 * The Docker image is built locally only; it is not pushed to a registry.
 *
 * Security Scan blocking policy
 * -----------------------------
 *   pip-audit: known vulnerabilities in requirements.txt fail the pipeline.
 *   Trivy: HIGH or CRITICAL findings with available fixes fail the gate.
 *   Unfixed Trivy findings are reported but do not block the build.
 *   The embedded pip vendor SBOM is excluded because it contains stale
 *   package-version metadata.
 */

pipeline {
    agent any

    environment {
        IMAGE_NAME = "securepulse"
        IMAGE_TAG  = "latest"
        VENV_DIR   = ".jenkins-venv"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: "10", artifactNumToKeepStr: "3"))
        timeout(time: 20, unit: "MINUTES")
        disableConcurrentBuilds()
        timestamps()
    }

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
                    set -eu
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
                    set -eu
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
                    echo "Tests FAILED - Docker build will be skipped."
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
                    set -eu
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
                    rm -f pip-audit-report.json trivy-report.json

                    # pip-audit: scan pinned Python dependencies.
                    echo "--- [1/2] pip-audit: scanning requirements.txt ---"
                    ${VENV_DIR}/bin/pip install pip-audit --quiet
                    set +e
                    ${VENV_DIR}/bin/pip-audit -r requirements.txt --progress-spinner off --format json --output pip-audit-report.json
                    PIP_AUDIT_STATUS=\$?
                    set -e

                    if [ "\$PIP_AUDIT_STATUS" -eq 0 ]; then
                        echo "pip-audit: PASSED - no known vulnerabilities in requirements.txt"
                    else
                        echo "pip-audit detected vulnerabilities or a scan error. Report saved for review."
                    fi

                    # Trivy: use its official Docker image instead of downloading a binary.
                    echo "--- [2/2] Trivy: scanning ${IMAGE_NAME}:${IMAGE_TAG} ---"
                    docker pull aquasec/trivy:0.76.0
                    docker volume create securepulse-trivy-cache >/dev/null

                    # Export the just-built image to the Jenkins workspace.
                    # The trap removes the archive even if a scan fails.
                    ARCHIVE_PATH="\${WORKSPACE}/.securepulse-image.tar"
                    trap 'rm -f "\$ARCHIVE_PATH"' EXIT
                    docker save --output "\$ARCHIVE_PATH" ${IMAGE_NAME}:${IMAGE_TAG}

                    # Read the archive from the existing Jenkins home volume.
                    # This assumes the standard job workspace path:
                    # /var/jenkins_home/workspace/SecurePulse_CI-CD
                    # First Trivy run writes its JSON report into the workspace.
                    docker run --rm \\
                        --mount type=volume,src=jenkins_home,dst=/workspace,volume-subpath=workspace/SecurePulse_CI-CD \\
                        --mount type=volume,src=securepulse-trivy-cache,dst=/root/.cache/trivy \\
                        aquasec/trivy:0.76.0 image \\
                        --cache-dir /root/.cache/trivy \\
                        --input /workspace/.securepulse-image.tar \\
                        --no-progress \\
                        --skip-files "**/pip/_vendor/bom.cdx.json" \\
                        --format json \\
                        --output /workspace/trivy-report.json \\
                        --exit-code 0 \\
                        --severity UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL

                    # Informational scan: print findings at all severities without blocking.
                    docker run --rm \\
                        --mount type=volume,src=jenkins_home,dst=/workspace,readonly,volume-subpath=workspace/SecurePulse_CI-CD \\
                        --mount type=volume,src=securepulse-trivy-cache,dst=/root/.cache/trivy \\
                        aquasec/trivy:0.76.0 image \\
                        --cache-dir /root/.cache/trivy \\
                        --input /workspace/.securepulse-image.tar \\
                        --no-progress \\
                        --skip-files "**/pip/_vendor/bom.cdx.json" \\
                        --exit-code 0 \\
                        --severity UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL

                    # Blocking scan: fail on fixable HIGH or CRITICAL findings.
                    echo "Trivy blocking scan (HIGH + CRITICAL with fixes available):"
                    docker run --rm \\
                        --mount type=volume,src=jenkins_home,dst=/workspace,readonly,volume-subpath=workspace/SecurePulse_CI-CD \\
                        --mount type=volume,src=securepulse-trivy-cache,dst=/root/.cache/trivy \\
                        aquasec/trivy:0.76.0 image \\
                        --cache-dir /root/.cache/trivy \\
                        --input /workspace/.securepulse-image.tar \\
                        --no-progress \\
                        --skip-files "**/pip/_vendor/bom.cdx.json" \\
                        --ignore-unfixed \\
                        --exit-code 1 \\
                        --severity HIGH,CRITICAL

                    # Validate report files after all scans have run.
                    test -s pip-audit-report.json
                    test -s trivy-report.json

                    if [ "\$PIP_AUDIT_STATUS" -ne 0 ]; then
                        echo "ERROR: pip-audit reported vulnerabilities or a scan error. Blocking deployment."
                        exit 1
                    fi

                    echo "Trivy: PASSED - no blocking HIGH or CRITICAL findings with available fixes in the scanned image components."
                """
            }
            post {
                always {
                    archiveArtifacts(
                        artifacts: 'pip-audit-report.json,trivy-report.json',
                        allowEmptyArchive: true,
                        fingerprint: true
                    )
                }
                success {
                    echo "Security Scan PASSED - pip-audit and Trivy found no blocking vulnerabilities."
                }
                failure {
                    echo "Security Scan FAILED - vulnerabilities or scanner errors detected. Deployment is blocked. Review scan output above."
                }
            }
        }

        
stage("Deploy SecurePulse") {
    steps {
        echo "==> Deploying ${IMAGE_NAME}:${IMAGE_TAG} as securepulse-app..."

        withCredentials([
            usernamePassword(
                credentialsId: 'securepulse-jenkins-api',
                usernameVariable: 'JENKINS_USER',
                passwordVariable: 'JENKINS_API_TOKEN'
            )
        ]) {
            sh '''
                set -eu

                # Stop and remove only the SecurePulse app container.
                if docker ps -a --filter "name=^securepulse-app$" --format '{{.Names}}' | grep -q '^securepulse-app$'; then
                    STATUS=$(docker inspect -f '{{.State.Status}}' securepulse-app)

                    if [ "$STATUS" = "running" ]; then
                        docker stop securepulse-app
                    fi

                    docker rm securepulse-app
                fi

                # Start SecurePulse with Jenkins API credentials.
                docker run -d \
                    --name securepulse-app \
                    --restart unless-stopped \
                    -p 5001:5000 \
                    -e JENKINS_USER="$JENKINS_USER" \
                    -e JENKINS_API_TOKEN="$JENKINS_API_TOKEN" \
                    securepulse:latest

                sleep 5

                STATUS=$(docker inspect -f '{{.State.Status}}' securepulse-app 2>/dev/null || echo "not_found")
                echo "Container status: $STATUS"

                if [ "$STATUS" != "running" ]; then
                    echo "ERROR: securepulse-app is not running."
                    docker logs securepulse-app || true
                    exit 1
                fi

                echo "Deployment verified on host port 5001."
            '''
        }
    }

    post {
        success {
            echo "Deploy stage PASSED - securepulse-app is live on port 5001."
        }
        failure {
            echo "Deploy stage FAILED - review the logs above."
        }
    }
}


    post {
        always {Deploy SecurePulse
            echo "==> Cleaning up virtual environment..."
            sh "rm -rf ${VENV_DIR}"
            echo "Pipeline finished. Status: ${currentBuild.currentResult}"
        }
        success {
            echo "BUILD SUCCEEDED - SecurePulse tests, image build, security scans, and deployment completed."
        }
        failure {
            echo "BUILD FAILED - review the stage logs above."
        }
        unstable {
            echo "BUILD UNSTABLE - some tests may have been skipped or flaky."
        }
    }
}
