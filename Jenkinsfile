
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
                    python3 -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    python3 -m pytest -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t ${DOCKER_IMAGE} .
                '''
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                    set -e

                    echo "Running pip-audit..."
                    pip-audit -r requirements.txt

                    echo "Running Trivy informational scan..."
                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v trivy-cache:/root/.cache/ \
                        aquasec/trivy:latest image \
                        --scanners vuln \
                        --exit-code 0 \
                        --severity UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL \
                        ${DOCKER_IMAGE}

                    echo "Running Trivy blocking scan..."
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
                    sshagent(credentials: ["${SSH_CREDENTIALS}"]) {
                        sh '''
                            set -e

                            echo "Saving Docker image..."
                            docker save ${DOCKER_IMAGE} | gzip > securepulse.tar.gz

                            echo "Copying image to EC2..."
                            scp -o StrictHostKeyChecking=no \
                                securepulse.tar.gz \
                                ${EC2_USER}@${EC2_HOST}:/tmp/securepulse.tar.gz

                            echo "Deploying application on EC2..."

                            printf '%s\\n' "$JENKINS_API_USER" "$JENKINS_API_TOKEN" | \
                            ssh -o StrictHostKeyChecking=no \
                                ${EC2_USER}@${EC2_HOST} '
                                    set -e

                                    read -r JENKINS_API_USER
                                    read -r JENKINS_API_TOKEN

                                    echo "Loading Docker image..."
                                    gunzip -c /tmp/securepulse.tar.gz | sudo docker load

                                    echo "Removing previous container..."
                                    sudo docker rm -f securepulse-app || true

                                    echo "Starting SecurePulse..."
                                    sudo docker run -d \
                                        --name securepulse-app \
                                        --restart unless-stopped \
                                        -p 80:5000 \
                                        -e JENKINS_URL=REPLACE_WITH_REACHABLE_JENKINS_URL \
                                        -e JENKINS_USER="$JENKINS_API_USER" \
                                        -e JENKINS_TOKEN="$JENKINS_API_TOKEN" \
                                        securepulse:latest

                                    echo "Checking application..."
                                    sleep 10
                                    curl -f http://localhost/

                                    rm -f /tmp/securepulse.tar.gz
                                    echo "Deployment successful!"
                                '
                        '''

                        sh 'rm -f securepulse.tar.gz'
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
