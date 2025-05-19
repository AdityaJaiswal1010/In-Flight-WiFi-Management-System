pipeline {
    agent any

    environment {
        VENV = 'env'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Using the repo already cloned by Jenkins SCM'
            }
        }

        stage('Setup Python') {
            steps {
                echo 'Creating virtual environment and installing requirements...'
                sh 'python3 -m venv env'
                sh './env/bin/pip install --upgrade pip'
                sh './env/bin/pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running API test cases...'
                sh 'export PYTHONPATH=$PYTHONPATH:$(pwd)'
                sh './env/bin/pip install pytest httpx'
                sh './env/bin/pytest tests/ --disable-warnings'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh 'docker build -t inflight-fastapi-app .' 
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying container...'
                sh 'docker stop inflight-fastapi-app || true'
                sh 'docker rm inflight-fastapi-app || true'
                sh 'docker run -d -p 8000:8000 --name inflight-fastapi-app inflight-fastapi-app'
            }
        }
    }

    post {
        success {
            echo 'Pipeline executed successfully.'
        }
        failure {
            echo 'Pipeline failed. Check test cases and build logs.'
        }
    }
}
