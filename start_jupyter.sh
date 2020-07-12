#! /bin/bash

IMAGE_NAME=$(cat .dockername)
TARGET_PORT=8888

docker run -it --rm \
    -p $TARGET_PORT:8888 \
    -e JUPYTER_ENABLE_LAB=yes \
    --name jpsimfaas \
    -v "$(pwd)":/home/jovyan/work \
    $IMAGE_NAME
