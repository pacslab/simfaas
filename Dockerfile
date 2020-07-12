FROM jupyter/datascience-notebook:latest

USER root

# Install Pandoc
# Update with latest version every once in a while: https://github.com/jgm/pandoc/releases/
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        wget ca-certificates openssh-client \
    && wget https://github.com/jgm/pandoc/releases/download/2.10/pandoc-2.10-1-amd64.deb -O pandoc-amd64.deb \
    && dpkg -i pandoc-amd64.deb \
    && rm pandoc-amd64.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER $NB_USER

# Install extensions and enable spellchecker
RUN pip install jupyter_contrib_nbextensions && \
    jupyter contrib nbextension install --user && \
    # can modify or enable additional extensions here
    jupyter nbextension enable spellchecker/main --user

# example requirements
ADD examples/requirements.txt /simfaas/ex-requirements.txt
RUN pip install -r /simfaas/ex-requirements.txt
# Plotly for Jupyter
RUN pip install jupyterlab "ipywidgets==7.5" \
    && jupyter labextension install jupyterlab-plotly@4.8.2 \
    && jupyter labextension install @jupyter-widgets/jupyterlab-manager plotlywidget@4.8.2
# copy simfaas
ADD requirements.txt /simfaas/
RUN pip install -r /simfaas/requirements.txt
ADD simfaas /simfaas/simfaas
ADD README.rst /simfaas/
ADD *.py /simfaas/
# Install simfaas
RUN pip install /simfaas
