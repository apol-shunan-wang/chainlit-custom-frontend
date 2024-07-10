# https://hub.docker.com/_/python
FROM python:3.12.4-slim-bookworm

ARG USERNAME=vscode
ARG USER_UID
ARG USER_GID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

ENV TZ="Asia/Tokyo"

RUN apt-get update -y
RUN apt-get install -y git

# pip
RUN pip install --upgrade pip
COPY .devcontainer/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

USER $USERNAME
