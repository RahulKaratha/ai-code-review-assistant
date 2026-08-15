pipeline {

    agent none

    options {
        buildDiscarder(logRotator(
            numToKeepStr: '20',
            artifactNumToKeepStr: '10'
        ))
        disableConcurrentBuilds()
    }

    stages {

        stage('Continuous Integration') {

            agent {
                docker {
                    image 'rahulkaratha/ai-review-ci:latest'
                    args '-u root:root'
                }
            }

            stages {

                stage('Checkout') {
                    steps {
                        echo 'Repository checked out automatically.'
                    }
                }

                stage('Verify Python') {
                    steps {
                        sh 'python --version'
                    }
                }

                stage('Lint Code') {
                    steps {
                        sh 'ruff check .'
                    }
                }

                stage('Security Scan') {
                    steps {
                        sh 'bandit -r app -x tests,__pycache__,.pytest_cache'
                    }
                }

                stage('Run Tests') {
                    steps {
                        sh '''
                            pytest \
                                --cov=app \
                                --cov-report=xml \
                                --junitxml=test-results.xml
                        '''
                    }
                }
            }

            post {
                always {
                    junit 'test-results.xml'
                    archiveArtifacts(
                        artifacts: 'coverage.xml',
                        fingerprint: true
                    )
                }
            }
        }

        stage('Continuous Delivery') {

            agent any

            environment {
                DOCKER_IMAGE          = 'rahulkaratha/ai-code-review-assistant'
                DOCKER_CONTAINER_NAME = 'ai-code-review-container'
                EC2_HOST              = '18.60.214.249'
                EC2_USERNAME          = 'ec2-user'
            }

            stages {

                stage('Build Docker Image') {
                    steps {
                        sh '''
                            docker build \
                                -t ${DOCKER_IMAGE}:latest \
                                -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
                        '''
                    }
                }

                stage('Trivy Image Scan') {
                    steps {
                        sh '''
                            export DOCKER_HOST=tcp://host.docker.internal:2375

                            mkdir -p reports

                            echo "Generating text report..."

                            trivy image \
                                --severity HIGH,CRITICAL \
                                --no-progress \
                                --format table \
                                --output reports/trivy-report.txt \
                                ${DOCKER_IMAGE}:${BUILD_NUMBER}

                            echo "Generating HTML report..."

                            trivy image \
                                --severity HIGH,CRITICAL \
                                --no-progress \
                                --format template \
                                --template "@trivy/html.tpl" \
                                --output reports/trivy-report.html \
                                ${DOCKER_IMAGE}:${BUILD_NUMBER}

                            echo "===== Trivy Summary ====="

                            cat reports/trivy-report.txt
                        '''
                    }
                }

                stage('Push Docker Image') {
                    steps {
                        withCredentials([
                            usernamePassword(
                                credentialsId: 'dockerhub',
                                usernameVariable: 'DOCKER_USER',
                                passwordVariable: 'DOCKER_PASS'
                            )
                        ]) {
                            sh '''
                                echo "$DOCKER_PASS" | docker login \
                                    -u "$DOCKER_USER" \
                                    --password-stdin

                                docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                                docker push ${DOCKER_IMAGE}:latest

                                docker logout
                            '''
                        }
                    }
                }

                stage('Deploy to EC2') {
                    steps {
                        withCredentials([
                            sshUserPrivateKey(
                                credentialsId: 'ec2-ssh',
                                keyFileVariable: 'PRIVATE_KEY_FILE'
                            )
                        ]) {
                            sh '''
                                ssh -i "$PRIVATE_KEY_FILE" \
                                    -o StrictHostKeyChecking=no \
                                    ${EC2_USERNAME}@${EC2_HOST} '

                                    echo "===== Pulling New Image ====="

                                    docker pull '"${DOCKER_IMAGE}:${BUILD_NUMBER}"'

                                    echo "===== Deploying New Version ====="

                                    docker rm -f '"${DOCKER_CONTAINER_NAME}"' || true

                                    docker run -d \
                                        --restart unless-stopped \
                                        --name '"${DOCKER_CONTAINER_NAME}"' \
                                        --env-file ~/ai-code-review.env \
                                        -p 80:8000 \
                                        '"${DOCKER_IMAGE}:${BUILD_NUMBER}"'
                                '
                            '''
                        }
                    }
                }

                stage('Verify Deployment') {
                    steps {
                        withCredentials([
                            sshUserPrivateKey(
                                credentialsId: 'ec2-ssh',
                                keyFileVariable: 'PRIVATE_KEY_FILE'
                            )
                        ]) {
                            script {

                                try {

                                    sh '''
                                        echo "Waiting for application to become healthy..."

                                        for i in $(seq 1 12); do
                                            if curl --fail http://${EC2_HOST}/health >/dev/null 2>&1; then
                                                echo "Deployment Successful!"
                                                exit 0
                                            fi

                                            echo "Attempt $i/12 failed. Retrying in 5 seconds..."
                                            sleep 5
                                        done

                                        echo "Deployment failed."
                                        exit 1
                                    '''

                                    sh """
                                        ssh -i "$PRIVATE_KEY_FILE" \
                                            -o StrictHostKeyChecking=no \
                                            ${EC2_USERNAME}@${EC2_HOST} \
                                            "echo '${DOCKER_IMAGE}:${BUILD_NUMBER}' > ~/.last_successful_image"
                                    """

                                } catch (Exception e) {

                                    echo 'Health check failed! Initiating rollback...'

                                    def previousImage = sh(
                                        script: '''
                                            ssh -i "$PRIVATE_KEY_FILE" \
                                                -o StrictHostKeyChecking=no \
                                                ${EC2_USERNAME}@${EC2_HOST} \
                                                "cat ~/.last_successful_image 2>/dev/null || true"
                                        ''',
                                        returnStdout: true
                                    ).trim()

                                    if (!previousImage) {
                                        error('No successful deployment available for rollback.')
                                    }

                                    echo "Rolling back to ${previousImage}"

                                    withEnv(["ROLLBACK_IMAGE=${previousImage}"]) {
                                        sh '''
                                            ssh -i "$PRIVATE_KEY_FILE" \
                                                -o StrictHostKeyChecking=no \
                                                ${EC2_USERNAME}@${EC2_HOST} '

                                                docker rm -f ${DOCKER_CONTAINER_NAME} || true

                                                docker run -d \
                                                    --restart unless-stopped \
                                                    --name ${DOCKER_CONTAINER_NAME} \
                                                    --env-file ~/ai-code-review.env \
                                                    -p 80:8000 \
                                                    '"${ROLLBACK_IMAGE}"'

                                                echo "Waiting for rollback application..."

                                                for i in $(seq 1 12); do
                                                    if curl --fail http://localhost:80/health >/dev/null 2>&1; then
                                                        echo "Rollback successful."
                                                        exit 0
                                                    fi

                                                    echo "Rollback attempt $i/12 failed. Waiting 5 seconds..."
                                                    sleep 5
                                                done

                                                echo "Rollback failed."
                                                exit 1
                                            '
                                        '''
                                    }

                                    error('Deployment failed. Rollback completed successfully.')

                                }
                            }
                        }
                    }
                }

                stage('Cleanup Local Images') {
                    steps {
                        sh '''
                            docker image rm ${DOCKER_IMAGE}:${BUILD_NUMBER} || true
                            docker image rm ${DOCKER_IMAGE}:latest || true
                        '''
                    }
                }
            }

            post {
                always {
                    archiveArtifacts(
                        artifacts: 'reports/trivy-report.txt,reports/trivy-report.html',
                        fingerprint: true
                    )
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Something went wrong.'
        }
    }
}
