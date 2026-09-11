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

        stage('Validar Ambiente') {
            steps {
                script {
                    if (params.DEPLOY_ENV == 'prod' && env.BRANCH_NAME != 'main') {
                        error "Solo la rama 'main' puede desplegar a producción (prod). Estás en la rama '${env.BRANCH_NAME}'."
                    }
                    if (params.DEPLOY_ENV == 'prod') {
                        input message: "¿Confirmas el despliegue a PRODUCCIÓN?", ok: "Sí, desplegar"
                    }
                }
            }
        }

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

                    # Build y Tag con Commit ID y Latest (latest es necesario porque
                    # los manifiestos de deployment/service arrancan con ese tag)
                    docker build \
                        -t localhost:5000/app-python:${IMAGE_TAG} \
                        -t localhost:5000/app-python:latest \
                        .

                    docker push localhost:5000/app-python:${IMAGE_TAG}
                    docker push localhost:5000/app-python:latest
                '''
            }
        }

        stage('Deploy') {
            steps {
                script {
                    // Guardamos el hash de la app ANTES de cambiar de repo
                    env.APP_COMMIT_TAG = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                }

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
                    kubectl apply \
                        --context ${TARGET_ENV} \
                        -f manifests/k8s/${TARGET_ENV}/app-python-deployment.yaml

                    kubectl set image \
                        --context ${TARGET_ENV} \
                        deployment/app-python \
                        app-python=host.docker.internal:5000/app-python:${APP_COMMIT_TAG} \
                        -n python

                    kubectl apply \
                        --context ${TARGET_ENV} \
                        -f manifests/k8s/${TARGET_ENV}/app-python-service.yaml

                    kubectl annotate deployment/app-python \
                        --context ${TARGET_ENV} \
                        -n python \
                        kubernetes.io/change-cause="Jenkins build #${BUILD_NUMBER} - commit ${APP_COMMIT_TAG}" \
                        --overwrite

                    echo "Para ver la app, corre en tu terminal: minikube service app-python-service -n python -p ${TARGET_ENV} --url"
                '''
            }
        }
    }
}
