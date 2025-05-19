pipeline {
    agent any

    environment {
        VENV = 'env'
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
                sh '''
                    /opt/homebrew/bin/python3.10 -m venv env
                    ./env/bin/pip install --upgrade pip
                    ./env/bin/pip install -r requirements.txt
                '''
            }
        }


        stage('Generate Prisma Client') {
            steps {
                echo 'Generating Prisma client...'
                sh '''
                    export PATH="$(./env/bin/python -m site --user-base)/bin:$PATH"
                    ./env/bin/python -m prisma generate
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running API test cases...'
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
            echo '✅ Pipeline executed successfully.'
        }
        failure {
            echo '❌ Pipeline failed. Please check logs above.'
        }
    }
}
