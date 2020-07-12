# Jupyter Docker Image

To ease the process of installation and experimenttion with `SimFaaS`, we developed
a docker image extending the [Jupyter Notebook Data Science Stack](https://hub.docker.com/r/jupyter/datascience-notebook/).
The resulting docker image is also available publicly on [Docker Hub](https://hub.docker.com/r/nimamahmoudi/jupyter-simfaas).

## Installation

The only requirement for running the jupyter notebook stack is `docker` which can easily be installed:

```sh
sudo apt-get update && sudo apt-get -y install docker.io

docker ps
sudo docker ps

sudo usermod -aG docker $USER
sudo chown "$USER":"$USER" /home/"$USER"/.docker -R
sudo chmod g+rwx "/home/$USER/.docker" -R
sudo chown "$USER":"$USER" /var/run/docker.sock
sudo chmod g+rwx /var/run/docker.sock -R
sudo systemctl enable docker
```

## Running

To run the jupyter lab in the `current directory`, simply run the following command:

```sh
IMAGE_NAME=nimamahmoudi/jupyter-simfaas # or $(cat .dockername) if in root folder of the github repo
TARGET_PORT=8888 # The port on which the jupyter notebook will run

docker run -it --rm \
    -p $TARGET_PORT:8888 \
    -e JUPYTER_ENABLE_LAB=yes \
    --name jpsimfaas \
    -v "$(pwd)":/home/jovyan/work \
    $IMAGE_NAME
```

The container logs will contain the token you need to log into your jupyter lab session.

## Building the Docker Image

In case you made changes to the library and wanted to build the docker image with your own changes,
you can run the following command.

```sh
IMAGE_NAME=nimamahmoudi/jupyter-simfaas # or $(cat .dockername) if in root folder of the github repo
docker build . -t $IMAGE_NAME
```
