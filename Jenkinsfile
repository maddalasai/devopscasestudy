pipeline {
    agent any

    environment {
        // CHANGE THESE TWO VALUES
        DOCKERHUB_USER = '141034durga'
GITHUB_REPO    = 'https://github.com/maddalasai/devopscasestudy.git'

        IMAGE_NAME = "${DOCKERHUB_USER}/booknest-reading-tracker"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: "${GITHUB_REPO}"
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:latest -t %IMAGE_NAME%:%BUILD_NUMBER% .'
            }
        }

        stage('Login to Docker Hub') {
            steps {
                // 'dockerhub-credentials' is the ID created in Jenkins (username + password/token)
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials',
                                                  usernameVariable: 'DH_USER',
                                                  passwordVariable: 'DH_PASS')]) {
                    bat 'echo %DH_PASS%| docker login -u %DH_USER% --password-stdin'
                }
            }
        }

        stage('Push Image to Docker Hub') {
            steps {
                bat 'docker push %IMAGE_NAME%:latest'
                bat 'docker push %IMAGE_NAME%:%BUILD_NUMBER%'
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                bat 'kubectl apply -f k8s/deployment.yaml'
                bat 'kubectl apply -f k8s/service.yaml'
                // Point the deployment at the new build so pods are replaced
                bat 'kubectl set image deployment/booknest-deployment booknest=%IMAGE_NAME%:%BUILD_NUMBER%'
                bat 'kubectl rollout status deployment/booknest-deployment'
            }
        }
    }

    post {
        always {
            bat 'docker logout'
        }
    }
}
