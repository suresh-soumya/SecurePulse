
/*
 * SecurePulse – Declarative Jenkins Pipeline
 *
 * Pipeline stages:
 *   1. Checkout
 *   2. Install Dependencies
 *   3. Run Tests
 *   4. Build Docker Image
 *   5. Security Scan (pip-audit + Trivy)
 *   6. Deploy to AWS EC2 using SSH
 *
 * Credentials required in Jenkins:
 *   aws-ec2-ssh          - SSH Username with private key
 *   securepulse-jenkins-api - Username with password/API token
 *
 * Security Scan blocking policy:
 *   pip-audit : Any known dependency vulnerability fails the pipeline.
 *   Trivy     : HIGH or CRITICAL image vulnerabilities fail the pipeline.
 */

pipeline {

    agent any

    environment {
        IMAGE_NAME = "securepulse"
        IMAGE_TAG  = "latest"
        VENV_DIR   = ".jenkins-venv"
        EC2_HOST   = "52.62.211.106"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: "10", artifactNumToKeepStr: "3"))
        timeout(time: 30, unit: "MINUTES")
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

                    PYTHON=\\$(command -v python3 || command -v python)
                    echo "Using Python: \\$PYTHON"
                    \\$PYTHON --version

                    \\$PYTHON -m venv ${VENV_DIR}
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

                    # pip-audit: scan Python dependencies.
                    echo "--- [1/2] pip-audit: scanning requirements.txt ---"

                    ${VENV_DIR}/bin/pip install pip-audit --quiet
                    ${VENV_DIR}/bin/pip-audit -r requirements.txt --progress-spinner off

                    echo "pip-audit: PASSED"

                    # Trivy: scan the Docker image.
                    echo "--- [2/2] Trivy: scanning ${IMAGE_NAME}:${IMAGE_TAG} ---"

                    docker pull aquasec/trivy:0.76.0
                    docker volume create securepulse-trivy-cache >/dev/null

                    ARCHIVE_PATH="\${WORKSPACE}/.securepulse-image.tar"
                    trap 'rm -f "\$ARCHIVE_PATH"' EXIT

                    docker save --output "\$ARCHIVE_PATH" ${IMAGE_NAME}:${IMAGE_TAG}

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

                    echo "Trivy blocking scan (HIGH + CRITICAL):"

                    docker run --rm \\
                        --mount type=volume,src=jenkins_home,dst=/workspace,readonly,volume-subpath=workspace/SecurePulse_CI-CD \\
                        --mount type=volume,src=securepulse-trivy-cache,dst=/root/.cache/trivy \\
                        aquasec/trivy:0.76.0 image \\
                        --cache-dir /root/.cache/trivy \\
                        --input /workspace/.securepulse-image.tar \\
                        --no-progress \\
                        --exit-code 1 \\
                        --severity HIGH,CRITICAL

                    echo "Trivy: PASSED"
                """
            }

            post {
                success {
                    echo "Security Scan PASSED."
                }

                failure {
                    echo "Security Scan FAILED. Deployment is blocked."
                }
            }
        }

        stage("Deploy SecurePulse") {
            steps {
                echo "==> Deploying SecurePulse to AWS EC2..."

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'aws-ec2-ssh',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    ),
                    usernamePassword(
                        credentialsId: 'securepulse-jenkins-api',
                        usernameVariable: 'JENKINS_USER',
                        passwordVariable: 'JENKINS_API_TOKEN'
                    )
                ]) {
                    sh '''
                        set -eu

                        ARCHIVE="securepulse-image.tar.gz"
                        trap 'rm -f "$ARCHIVE"' EXIT

                        echo "Saving Docker image..."
                        docker save "$IMAGE_NAME:$IMAGE_TAG" | gzip > "$ARCHIVE"

                        echo "Transferring image to AWS EC2..."

                        scp -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=accept-new \
                            "$ARCHIVE" \
                            "$SSH_USER@$EC2_HOST:/tmp/securepulse-image.tar.gz"

                        echo "Deploying application on EC2..."

                        printf '%s\\n' "$JENKINS_USER" "$JENKINS_API_TOKEN" |
                        ssh -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=accept-new \
                            "$SSH_USER@$EC2_HOST" '
                                set -eu

                                IFS= read -r JENKINS_USER
                                IFS= read -r JENKINS_API_TOKEN

                                echo "Loading Docker image..."
                                sudo docker load -i /tmp/securepulse-image.tar.gz

                                echo "Removing previous application container if present..."
                                if sudo docker ps -a --format "{{.Names}}" |
                                    grep -qx "securepulse-app"; then
                                    sudo docker rm -f securepulse-app
                                fi

                                echo "Starting updated SecurePulse container..."

                                sudo docker run -d \
                                    --name securepulse-app \
                                    --restart unless-stopped \
                                    -p 80:5000 \
                                    -e "JENKINS_USER=$JENKINS_USER" \
                                    -e "JENKINS_API_TOKEN=$JENKINS_API_TOKEN" \
                                    securepulse:latest

                                echo "Waiting for application startup..."
                                sleep 5

                                STATUS=$(sudo docker inspect \
                                    -f "{{.State.Status}}" securepulse-app)

                                echo "Container status: $STATUS"

                                if [ "$STATUS" != "running" ]; then
                                    echo "ERROR: SecurePulse container failed."
                                    sudo docker logs securepulse-app || true
                                    exit 1
                                fi

                                echo "Checking application HTTP response..."
                                curl -fsS http://localhost/ >/dev/null

                                sudo rm -f /tmp/securepulse-image.tar.gz

                                echo "AWS deployment verified successfully."
                                sudo docker ps --filter name=securepulse-app
                            '
                    '''
                }
            }

            post {
                success {
                    echo "Deploy stage PASSED - SecurePulse is live on AWS."
                    echo "Application URL: http://${EC2_HOST}"
                }

                failure {
                    echo "Deploy stage FAILED - review the deployment logs."
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
            echo "BUILD SUCCEEDED - tests, image build, security scans, and AWS deployment completed."
        }

        failure {
            echo "BUILD FAILED - review the stage logs above."
        }

        unstable {
            echo "BUILD UNSTABLE - review test results."
        }
    }
}
