pipeline {
    agent any

    environment {
        VENV = 'env'
        PYTHON_VERSION = '3.10.13'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                git url: 'https://github.com/AdityaJaiswal1010/In-Flight-WiFi-Management-System', branch: 'main'
            }
        }

        stage('Install Python 3.10 via pyenv') {
            steps {
                sh '''
                    curl https://pyenv.run | bash

                    export PATH="$HOME/.pyenv/bin:$PATH"
                    eval "$(pyenv init --path)"
                    eval "$(pyenv virtualenv-init -)"

                    pyenv install -s ${PYTHON_VERSION}
                    pyenv global ${PYTHON_VERSION}

                    python --version
                '''
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                sh '''
                    python3.10 -m venv env
                    ./env/bin/pip install --upgrade pip
                    ./env/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Generate Prisma Client') {
            steps {
                sh '''
                    ./env/bin/pip install "prisma-client-py<0.11"
                    ./env/bin/prisma generate
                '''
            }
        }


        stage('Run Tests') {
            steps {
                sh '''
                    ./env/bin/pip install pytest httpx
                    ./env/bin/pytest tests/ --disable-warnings
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t inflight-fastapi-app .'
            }
        }

        stage('Deploy') {
            steps {
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
