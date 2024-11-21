# recipe-app-api
Recipe API (Udemy)

In Dockerhub settings/Personal access tokens create new token.
In GitHub repository settings/secrets/action create new secret DOCKER_USER, input Dockerhub username, create new secret
DOCKER_TOKEN copy GitHub token.

Create requirements.txt - 
Django>=3.2.4,<3.3
djangorestframework>=3.12.4,<3.13

Create Dockerfile - 
FROM python:3.9-alpine3.13
LABEL maintainer="ilia6260@gmail.com"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/ pip install -r requirements.txt && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        gjango-user

ENV PATH="/py/bin:$PATH"

USER django-user

Create .dockerignore - 
# Git
.git
.gitignore

# Docker
.docker

# Python
app/__pycache__/
app/*/__pycache__/
app/*/*/__pycache__/
app/*/*/*/__pycache__/
.env/
.venv/
venv/

Create directory /app
run docker build .