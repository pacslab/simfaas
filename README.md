# Serverless Performance Simulator

![PyPI](https://img.shields.io/pypi/v/pacs-sls-sim.svg)
![PyPI - Status](https://img.shields.io/pypi/status/pacs-sls-sim.svg)
![Travis (.com)](https://img.shields.io/travis/com/nimamahmoudi/serverless-performance-simulator.svg)
![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/pacs-sls-sim.svg)
![GitHub](https://img.shields.io/github/license/nimamahmoudi/serverless-performance-simulator.svg)

This is a project done in [PACS Lab](https://pacs.eecs.yorku.ca/) aiming to develop
a performance simulator for serverless computing platforms. Using this simulator,
we can calculate Quality of Service (QoS) metrics like average response time,
average probability of cold start, average running servers (directly reflecting average cost),
histogram of different events, distribution of number of servers throughout time, and many
other characteristics.

The developed performance model can be used to debug/improve analytical performance models,
try new and improved management schema, or dig up a whole lot of properties of a common
modern scale-per request serverless platforms.

## Artifacts

- PyPi: comming soon...
- Github Repo: comming soon...
- Documentation: comming soon...
- Examples: comming soon...

## Requirements

- Python 3.6 or above
- PIP

## Installation

Install using pip:

```sh
pip install pacs-sls-sim
```

Upgrading using pip:

```sh
pip install pacs-sls-sim --upgrade
```

For installation in development mode:

```sh
git clone https://github.com/nimamahmoudi/serverless-performance-simulator
cd serverless-performance-simulator
pip install -e .
```

## Usage

comming soon...

## Development

In case you are interested in improving this work, you are always welcome to open up a pull request.
In case you need more details or explanation, contact me.

To get up and running with the environment, run the following after installing `Anaconda`:

```sh
conda env create -f simenv.yml
conda activate simenv
pip install -r requirements.txt
```

After updating the README.md, use the following to update the README.rst accordingly:

```sh
bash .travis/readme_prep.sh
```

To update the base devcontainer image, run the following in the project root (replace the docker hub username with yours, also update the docker image for base in `.devcontainer/Dockerfile`):

```sh
bash .devcontainer/build-push.sh
```

## Examples

```py
# comming soon...
```

## License

Unless otherwise specified:

MIT (c) 2020 Nima Mahmoudi & Hamzeh Khazaei

## Citation

You can find the paper with details of the proposed model in [PACS lab website](https://pacs.eecs.yorku.ca/publications/). You can use the following bibtex entry:

```bib
Coming soon...
```
