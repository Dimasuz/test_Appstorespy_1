FROM ubuntu:22.04

MAINTAINER Dimasuz

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Moscow

RUN apt update \
    && apt install -y tzdata python3.10 python3-pip libpq-dev\
    && python3 -m pip install --upgrade pip \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /usr/src/app/requirements.txt
WORKDIR /usr/src/app
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

ENTRYPOINT bash run.sh
