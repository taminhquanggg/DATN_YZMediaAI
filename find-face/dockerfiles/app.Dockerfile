FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get -y install sudo
RUN apt-get install -y \
    python3.8 \
    python3-pip \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libpq-dev \
    && pip3 install poetry
RUN apt-get install -y p7zip-full
RUN apt-get install -y git

# RUN sudo pip install --default-timeout=100 future

RUN \
    groupadd -g 999 dckr && useradd -u 999 -g dckr -G sudo -m -s /bin/bash dckr && \
    sed -i /etc/sudoers -re 's/^%sudo.*/%sudo ALL=(ALL:ALL) NOPASSWD: ALL/g' && \
    sed -i /etc/sudoers -re 's/^root.*/root ALL=(ALL:ALL) NOPASSWD: ALL/g' && \
    sed -i /etc/sudoers -re 's/^#includedir.*/## **Removed the include directive** ##"/g' && \
    echo "dckr ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    echo "Customized the sudoers file for passwordless access to the dckr user!" && \
    echo "dckr user:";  su - dckr -c id

USER dckr
WORKDIR /src

COPY pyproject.toml /src/
# RUN poetry config installer.parallel false
# ENV PIP_DEFAULT_TIMEOUT=120
RUN poetry install --verbose

COPY init_model.py /src/
COPY . /src
# ENV PIP_DEFAULT_TIMEOUT=60
RUN poetry update --verbose
RUN poetry run python init_model.py
