/*
 * SecurePulse – Declarative Jenkins Pipeline
 * Stage 3: CI/CD with Jenkins
 *
 * Agent requirements
 * ------------------
 *   • Python 3  (python3 / python both tried; see Install Dependencies stage)
 *   • pip       (bundled with Python 3.4+)
 *   • Docker    (daemon must be running; Jenkins user needs docker group access)
 *
 * No credentials or secrets are hardcoded.
 * The Docker image is built locally only – no push to any registry.
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
