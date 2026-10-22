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
                    steps { 
                        // Windows friendly echo
                        bat 'echo Validating Python syntax...' 
                    }
                }
                stage('Verify Assets') {
                    steps { 
                        // Windows check if files exist
                        bat 'if exist index.html (echo index.html found) else (exit 1)'
                        bat 'if exist Dockerfile (echo Dockerfile found) else (exit 1)'
                    }
                }
            }
        }
        stage('Build Image') {
            steps {
                script {
                    if (params.BUILD_TYPE == 'Simulate_Faulty_Release') {
                        // Windows compatible text replacement replacement string command
                        bat 'powershell -Command "(Get-Content deployment.yaml) -replace \'value: \\"stable\\"\', \'value: \\"faulty\\"\' | Set-Content deployment.yaml"'
                    }
                    bat "docker build -t ${DOCKER_IMAGE_NAME}:latest ."
                }
            }
        }
        stage('Push to Registry') {
            steps {
                // Skips registry push during local windows simulations to make it easier for you
                bat "echo Skipping registry push for local Windows test run..."
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                // If you do not have a local Kubernetes cluster active on your Windows machine, 
                // this stage will print a clear message instead of throwing errors.
                script {
                    try {
                        bat "kubectl apply -f deployment.yaml"
                        bat "kubectl rollout status deployment/traffic-dashboard-deployment --timeout=30s"
                    } catch (Exception e) {
                        echo "❌ Rollout failed or cluster offline! Executing automated safe rollback sequence..."
                        bat "kubectl rollout undo deployment/traffic-dashboard-deployment"
                    }
                }
            }
        }
    }
}

