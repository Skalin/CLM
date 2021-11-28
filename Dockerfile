# syntax=docker/dockerfile:1

FROM python:3.7-slim-buster

LABEL org.opencontainers.image.authors="500352@mail.muni.cz, 133@muni.cz, dominikskala@seznam.cz"

COPY requirements.txt requirements.txt

WORKDIR /app

COPY app/ /app
COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

COPY main.py /main.py

CMD ["python3", "/main.py"]