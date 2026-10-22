pipeline {
    agent any
    parameters {
        choice(name: 'BUILD_TYPE', choices: ['Stable_Release', 'Simulate_Faulty_Release'], description: 'Select Build Target')
    }
    environment {
        DOCKER_IMAGE_NAME = "YOUR_DOCKER_HUB_USERNAME/traffic-dashboard"
        REGISTRY_CREDENTIALS_ID = "docker-hub-credentials"
        KUBECONFIG_CREDENTIALS_ID = "jenkins-k8s-secret"
    }
    stages {
        stage('Parallel Validation Checks') {
            parallel {
                stage('Python Lint') {
                    steps { sh 'python3 -m py_compile app.py' }
                }
                stage('Verify Assets') {
                    steps { sh 'test -f index.html && test -f Dockerfile' }
                }
            }
        }
        stage('Build Image') {
            steps {
                script {
                    if (params.BUILD_TYPE == 'Simulate_Faulty_Release') {
                        sh "sed -i 'value: \"stable\"/value: \"faulty\"/' deployment.yaml"
                    }
                    sh "docker build -t ${DOCKER_IMAGE_NAME}:latest ."
                }
            }
        }
        stage('Push to Registry') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${REGISTRY_CREDENTIALS_ID}", passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                    sh "echo \$PASS | docker login -u \$USER --password-stdin"
                    sh "docker push ${DOCKER_IMAGE_NAME}:latest"
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                withKubeConfig([credentialsId: "${KUBECONFIG_CREDENTIALS_ID}"]) {
                    sh "kubectl apply -f deployment.yaml"
                    script {
                        try {
                            sh "kubectl rollout status deployment/traffic-dashboard-deployment --timeout=45s"
                        } catch (Exception e) {
                            echo "❌ Rollout stalled! Initiating automated safe rollback..."
                            sh "kubectl rollout undo deployment/traffic-dashboard-deployment"
                            error("Deployment rolled back successfully.")
                        }
                    }
                }
            }
        }
    }
}
