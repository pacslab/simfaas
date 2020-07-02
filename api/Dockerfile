FROM python:3.6-slim

# Create the user that will run the app
RUN adduser --disabled-password --gecos '' api-user

ENV PACSSIM_VER=${PACSSIM_VER:-0.1.4}

# Install pip
RUN pip install --upgrade pip
# Install requirements
ADD src/requirements.txt /opt/requirements.txt
RUN pip install -r /opt/requirements.txt

# Install simfaas
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get -y install --no-install-recommends gcc build-essential \
    # we need gcc for this pip
    && pip install simfaas==$PACSSIM_VER \
    # remove extra packages
    && apt-get purge -qy gcc build-essential \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*
ENV DEBIAN_FRONTEND=dialog

# add source files
ADD src /opt/api/

WORKDIR /opt/api
RUN chmod +x /opt/api/run.sh
RUN chown -R api-user:api-user ./

USER api-user

EXPOSE 5000

CMD ["bash", "./run.sh"]
