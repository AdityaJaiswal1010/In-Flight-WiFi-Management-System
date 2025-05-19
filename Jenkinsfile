pipeline {
    agent any

    environment {
        VENV = 'env'
        PYTHON_PATH = '/opt/homebrew/bin/python3.10'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                git url: 'https://github.com/AdityaJaiswal1010/In-Flight-WiFi-Management-System', branch: 'main'
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                echo 'Setting up virtual environment...'
                sh '''
                    ${PYTHON_PATH} -m venv ${VENV}
                    ./env/bin/pip install --upgrade pip
                    ./env/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Generate Prisma Client') {
            steps {
                echo 'Generating Prisma client...'
                sh '''
                    ./env/bin/pip install prisma-client-py
                    ./env/bin/prisma-client-py generate
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running API tests...'
                sh '''
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
                sh '''
                    docker stop inflight-fastapi-app || true
                    docker rm inflight-fastapi-app || true
                    docker run -d -p 8000:8000 --name inflight-fastapi-app inflight-fastapi-app
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Please check the logs above.'
        }
    }
}
