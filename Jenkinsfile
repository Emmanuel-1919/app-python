pipeline {
    agent any

    parameters {
        choice(
            name: 'DEPLOY_ENV',
            choices: ['dev', 'qa', 'prod'],
            description: 'Ambiente al que se va a desplegar'
        )
    }

    environment {
        TARGET_ENV = "${params.DEPLOY_ENV}"
    }

    stages {
        stage('Test') {
            agent {
                docker { image 'python:3.12-slim' }
            }
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip3 install -r requirements-dev.txt
                    pytest
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Construyendo imagen Docker...'
                sh '''
                    IMAGE_TAG=$(git rev-parse --short HEAD)

                    docker build \
                        -t localhost:5000/app-python:${IMAGE_TAG} \
                        .

                    docker push \
                        localhost:5000/app-python:${IMAGE_TAG}
                '''
            }
        }

        stage('Deploy') {
            steps {
                dir('manifests') {
                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: '*/main']],
                        userRemoteConfigs: [[
                            url: 'git@github.com:Emmanuel-1919/Devops-cicd.git',
                            credentialsId: 'github-devops-cicd'
                        ]]
                    ])
                }

                echo "Desplegando en el ambiente: ${TARGET_ENV}"

                sh '''
                    IMAGE_TAG=$(git rev-parse --short HEAD)

                    kubectl apply \
                        --context ${TARGET_ENV} \
                        -f manifests/k8s/${TARGET_ENV}/app-python-deployment.yaml

                    kubectl set image \
                        --context ${TARGET_ENV} \
                        deployment/app-python \
                        app-python=host.docker.internal:5000/app-python:${IMAGE_TAG} \
                        -n ${TARGET_ENV}

                    kubectl apply \
                        --context ${TARGET_ENV} \
                        -f manifests/k8s/${TARGET_ENV}/app-python-service.yaml
                '''
            }
        }
    }
}
