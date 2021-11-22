# syntax=docker/dockerfile:1

FROM python:3.7-slim-buster

MAINTAINER Dominik Skála "dominikskala@seznam.cz"

COPY requirements.txt requirements.txt

WORKDIR /

RUN pip3 install -r requirements.txt

COPY app/ /app
COPY main.py /main.py



CMD ["python3", "/main.py"]