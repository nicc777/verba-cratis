# Dockerfile adopted from the example here: https://stackoverflow.com/questions/48543834/how-do-i-reduce-a-python-docker-image-size-using-a-multi-stage-build
# Credit to https://stackoverflow.com/users/1668328/gcoh

#FROM python:2.7-alpine as base
FROM python:3.10-slim as base

RUN mkdir /svc
COPY . /svc
WORKDIR /svc

# RUN apk add --update \
#     postgresql-dev \
#     gcc \
#     musl-dev \
#     linux-headers

RUN pip3 install wheel && pip wheel . --wheel-dir=/svc/wheels

# FROM python:2.7-alpine
FROM python:3.10-slim

COPY --from=base /svc /svc

WORKDIR /svc

RUN pip3 install --no-index --find-links=/svc/wheels -r requirements.txt