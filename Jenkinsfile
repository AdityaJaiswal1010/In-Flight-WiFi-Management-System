pipeline {
    agent any

    environment {
        VENV = 'env'
        PATH = "/usr/local/bin:$PATH"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                git url: 'https://github.com/AdityaJaiswal1010/In-Flight-WiFi-Management-System', branch: 'main'
            }
        }

        stage('Setup Python') {
            steps {
                echo 'Creating virtual environment and installing requirements...'
                sh '''
                    python3 -m venv env
                    ./env/bin/pip install --upgrade pip
                    ./env/bin/pip install -r requirements.txt
                    export PATH="$PATH:$(./env/bin/python -m site --user-base)/bin"
                    ./env/bin/python -m prisma generate
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running API test cases...'
                sh '''
                    export PYTHONPATH=$(pwd)
                    ./env/bin/pip install pytest httpx
                    ./env/bin/pytest tests/ --disable-warnings
                '''
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
