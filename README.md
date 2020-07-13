# SimFaaS: A Serverless Performance Simulator

[![dockeri.co](https://dockeri.co/image/nimamahmoudi/jupyter-simfaas)](https://hub.docker.com/r/nimamahmoudi/jupyter-simfaas)

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pacslab/simfaas/master?urlpath=lab%2Ftree%2Fexamples%2F)
[![PyPI](https://img.shields.io/pypi/v/simfaas.svg)](https://pypi.org/project/simfaas/)
![PyPI - Status](https://img.shields.io/pypi/status/simfaas.svg)
![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/simfaas.svg)
![GitHub](https://img.shields.io/github/license/pacslab/simfaas.svg)


![PyPi Upload](https://github.com/pacslab/simfaas/workflows/PyPi%20Upload/badge.svg)
![API Docker CI](https://github.com/pacslab/simfaas/workflows/API%20Docker%20CI/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/simfaas/badge/?version=latest)](https://simfaas.readthedocs.io/en/latest/?badge=latest)

This is a project done in [PACS Lab](https://pacs.eecs.yorku.ca/) aiming to develop a performance simulator for serverless computing platforms. Using this simulator, we can calculate Quality of Service (QoS) metrics like average response time, the average probability of cold start, average running servers (directly reflecting average cost), a histogram of different events, distribution of the number of servers throughout time, and many other characteristics.

The developed performance model can be used to debug/improve analytical performance models, try new and improved management schema, or dig up a whole lot of properties of a common modern scale-per-request serverless platform.

## Artifacts

- [PyPi Package](https://pypi.org/project/simfaas/)
- [Github Repo](https://github.com/pacslab/simfaas)
- [ReadTheDocs Documentation](https://simfaas.readthedocs.io/en/latest/) ([PDF](https://simfaas.readthedocs.io/_/downloads/en/latest/pdf/))
- [Examples](./examples) ([MyBinder Jupyter Lab](https://mybinder.org/v2/gh/pacslab/simfaas/master?urlpath=lab%2Ftree%2Fexamples%2F))
- [Jupyter Notebook Docker Image](https://hub.docker.com/r/nimamahmoudi/jupyter-simfaas)

## Requirements

- Python 3.6 or above
- PIP

## Installation

Install using pip:

```sh
pip install simfaas
```

Upgrading using pip:

```sh
pip install simfaas --upgrade
```

For installation in development mode:

```sh
git clone https://github.com/pacslab/simfaas
cd simfaas
pip install -e .
```

And in case you want to be able to execute the examples:

```sh
pip install -r examples/requirements.txt
```

## Running in Docker

To ease the process of installation and experimenttion with `SimFaaS`, we developed
a docker image extending the [Jupyter Notebook Data Science Stack](https://hub.docker.com/r/jupyter/datascience-notebook/).
The resulting docker image is also available publicly on [Docker Hub](https://hub.docker.com/r/nimamahmoudi/jupyter-simfaas).

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

## Usage

A simple usage of the serverless simulator is shown in the following:

```py
from simfaas.ServerlessSimulator import ServerlessSimulator as Sim

sim = Sim(arrival_rate=0.9, warm_service_rate=1/1.991, cold_service_rate=1/2.244,
            expiration_threshold=600, max_time=1e6)
sim.generate_trace(debug_print=False, progress=True)
sim.print_trace_results()
```

Which prints an output similar to the following:

```
100%|██████████| 1000000/1000000 [00:42<00:00, 23410.45it/s]
Cold Starts / total requests:	 1213 / 898469
Cold Start Probability: 	     0.0014
Rejection / total requests:      0 / 898469
Rejection Probability: 		     0.0000
Average Instance Life Span:      6335.1337
Average Server Count:  		     7.6612
Average Running Count:  	     1.7879
Average Idle Count:  		     5.8733
```

Using this information, you can predict the behaviour of your system in production.

## Development

In case you are interested in improving this work, you are always welcome to open up a pull request.
In case you need more details or explanation, contact me.

To get up and running with the environment, run the following after installing `Anaconda`:

```sh
conda env create -f environment.yml
conda activate simenv
pip install -r requirements.txt
pip install -e .
```

After updating the README.md, use the following to update the README.rst accordingly:

```sh
bash .travis/readme_prep.sh
```

## Examples

Some of the possible use cases of the serverless performance simulator are shown in the `examples` folder in our Github repository.

## License

Unless otherwise specified:

MIT (c) 2020 Nima Mahmoudi & Hamzeh Khazaei

## Citation

You can find the paper with details of the simultor in [PACS lab website](https://pacs.eecs.yorku.ca/publications/). You can use the following bibtex entry for citing our work:

```bib
Coming Soon...
```
