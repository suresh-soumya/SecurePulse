
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

                    echo "Saving Docker image..."
                    docker save ${DOCKER_IMAGE} | gzip > securepulse.tar.gz

                    echo "Copying image to EC2..."
                    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no \
                        securepulse.tar.gz \
                        ${EC2_USER}@${EC2_HOST}:/tmp/securepulse.tar.gz

                    echo "Deploying application on EC2..."

                    printf '%s\\n' "$JENKINS_API_USER" "$JENKINS_API_TOKEN" | \
                    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
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
                               -e JENKINS_URL="https://relight-rental-undead.ngrok-free.dev" \
                                -e JENKINS_USER="$JENKINS_API_USER" \
                                -e JENKINS_TOKEN="$JENKINS_API_TOKEN" \
                                securepulse:latest

                            echo "Checking application..."
                            sleep 10
                            curl -f http://localhost/

                            rm -f /tmp/securepulse.tar.gz
                            echo "Deployment successful!"
                        '

                    rm -f securepulse.tar.gz
                '''
            }
        }
    }
}
