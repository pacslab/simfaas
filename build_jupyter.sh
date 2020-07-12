#! /bin/bash

IMAGE_NAME=$(cat .dockername)
docker build . -t $IMAGE_NAME
