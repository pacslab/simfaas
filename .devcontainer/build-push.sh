export DOCKER_IMAGE=nimamahmoudi/vsc-serverless-performance-simulator
docker build -f .devcontainer/Dockerfile-base -t $DOCKER_IMAGE . && \
    docker push $DOCKER_IMAGE
