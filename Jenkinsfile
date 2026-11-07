
pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'securepulse:latest'
        EC2_HOST = '13.55.36.114'
        EC2_USER = 'ubuntu'
        SSH_CREDENTIALS = 'aws-ec2-ssh'
        JENKINS_API_CREDENTIALS = 'securepulse-jenkins-api'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/suresh-soumya/SecurePulse.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    set -e
                    python3 -m venv .venv
                    .venv/bin/python -m pip install --upgrade pip
                    .venv/bin/pip install -r requirements.txt
                    .venv/bin/pip install pytest pip-audit
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '.venv/bin/python -m pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${DOCKER_IMAGE} .'
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                    set -e
                    .venv/bin/pip-audit -r requirements.txt

                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v trivy-cache:/root/.cache/ \
                        aquasec/trivy:latest image \
                        --scanners vuln \
                        --exit-code 0 \
                        --severity UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL \
                        ${DOCKER_IMAGE}

                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v trivy-cache:/root/.cache/ \
                        aquasec/trivy:latest image \
                        --scanners vuln \
                        --ignore-unfixed \
                        --exit-code 1 \
                        --severity HIGH,CRITICAL \
                        ${DOCKER_IMAGE}

                    echo "Security Scan PASSED."
                '''
            }
        }

        stage('Deploy SecurePulse') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: "${JENKINS_API_CREDENTIALS}",
                        usernameVariable: 'JENKINS_API_USER',
                        passwordVariable: 'JENKINS_API_TOKEN'
                    )
                ]) {
                    withCredentials([sshUserPrivateKey(
                        credentialsId: "${SSH_CREDENTIALS}",
                        keyFileVariable: 'SSH_KEY'
                    )]) {
                        sh '''
                            set -e

                            docker save ${DOCKER_IMAGE} | gzip > securepulse.tar.gz

                            scp -i "$SSH_KEY" -o StrictHostKeyChecking=no \
                                securepulse.tar.gz \
                                ${EC2_USER}@${EC2_HOST}:/tmp/securepulse.tar.gz

                            printf '%s\\n' "$JENKINS_API_USER" "$JENKINS_API_TOKEN" | \
                            ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
                                ${EC2_USER}@${EC2_HOST} '
                                    set -e
                                    read -r JENKINS_API_USER
                                    read -r JENKINS_API_TOKEN

                                    gunzip -c /tmp/securepulse.tar.gz | sudo docker load
                                    sudo docker rm -f securepulse-app || true

                                    sudo docker run -d \
                                        --name securepulse-app \
                                        --restart unless-stopped \
                                        -p 80:5000 \
                                        -e JENKINS_URL="https://relight-rental-undead.ngrok-free.dev" \
                                        -e JENKINS_USER="$JENKINS_API_USER" \
                                        -e JENKINS_TOKEN="$JENKINS_API_TOKEN" \
                                        securepulse:latest

                                    sleep 10
                                    curl -f http://localhost/
                                    rm -f /tmp/securepulse.tar.gz
                                '

                            rm -f securepulse.tar.gz
                            echo "Deployment successful!"
                        '''
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'SecurePulse pipeline completed successfully!'
        }
        failure {
            echo 'SecurePulse pipeline failed. Check the stage logs.'
        }
        always {
            echo 'Pipeline execution finished.'
        }
    }
}
