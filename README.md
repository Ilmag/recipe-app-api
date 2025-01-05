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
# Dockerfile
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
# End Dockerfile

Create .dockerignore -
# .dockerignore
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
# End .dockerignore

Create directory /app
run docker build .

Create docker-compose.yml - 
# docker-compose.yml
version: "3.9"

services:
  app:
    build:
      context: .
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app
    command: >
      sh -c "python manage.py runserver 0.0.0.0:8000"
# End docker-compose.yml

run docker-compose build

Create requirements.dev.txt - (adding linting)
# requirements.dev.txt
flake8>=3.9.2,<3.10
# End requirements.dev.txt

In docker-compose.yml after "context: ." add new lines:
"      args:
        - DEV=true"

In Dockerfile after "COPY ./requirements.txt /tmp/requirements.txt" add line:
"COPY ./requirements.dev.txt /tmp/requirements.dev.txt"
above "RUN python -m venv /py && \" add:
"ARG DEV=false"

In Dockerfile after "/py/bin/pip install -r /tmp/requirements.txt && \" add lines:
"if [ $DEV = "true" ]; \
      then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \"
run docker-compose build

Inside the app directory create file .flake8:
# .flake8

[flake8]
exclude =
  migrations,
  __pycache__,
  manage.py,
  settings.py
# END .flake8

run docker-compose run --rm app sh -c "flake"

Create project:
docker-compose run --rm app sh -c "django-admin startproject app ."

run docker-compose up

******* GitHub Actions *******

Create .github/workflows/checks.yml
# checks.yml
on: [push]

jobs:
  test-lint:
    name: Test and Lint
    runs-on: ubuntu-20.04
    steps:
      - name: Login to Docker Hub
        uses: docker/login-action@v1
        with:
          username: ${{ secrets.DOCKERHUB_USER }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - name: Checkout
        uses: actions/checkout@v2
      - name: Test
        run: docker compose run --rm app sh -c "python manage.py test"
      - name: Lint
        run: docker compose run --rm app sh -c "flake8"
# End checks.yml

Commit and push.

Remove version line in docker-compose.yml

******* TDD with *******
******* DB *******
In docker-compose.yml after sh -c "python manage.py runserver 0.0.0.0:8000" add:
# docker-compose.yml
    environment:
      - DB_HOST=db
      - DB_NAME=devdb
      - DB_USER=devuser
      - DB_PASS=changeme
    depends_on:
      - db

  db:
    image: postgres:13-alpine
    volumes:
      - dev-db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=devdb
      - POSTGRES_USER=devuser
      - POSTGRES_PASSWORD=changeme
# END docker-compose.yml

In Dockerfile after /py/bin/pip install --upgrade pip && \ add:

apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \

after rm -rf /tmp && \ add:

apk del .tmp-build-deps && \

In requirements.txt add:

psycopg2>=2.8.6,<2.9

Run:

docker-compose down
docker-compose build

In app/app/settings.py add:

import os

edit:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('DB_HOST'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS'),
    }
}

***Create core app***

Run:

docker-compose run --rm app sh -c "python manage.py startapp core"

In core delete tests.py, views.py, create dir tests, add __init__.py to tests. Add core to settings installed apps.

***Fixing DB race***

In core create management/commands/wait_for_db.py (__init__.py in both directories):

"""
Django command to wait for the database to be available.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        pass

Create tests/test_commands.py:

# Start
"""
Test custom Django management commands.
"""
from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2OpError

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready."""
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

# End

Run:

docker-compose run --rm app sh -c "python manage.py test"

Test fails - wait_for_db.py not implemented yet.

Add negative test case:

@patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError."""
        patched_check.side_effect = [Psycopg2OpError] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])

edit wait_for_db.py:

"""
Django command to wait for the database to be available.
"""
import time

from psycopg2 import OperationalError as Psycopg2OpError # noqa

from django.db.utils import OperationalError # noqa
from django.core.management.base import BaseCommand # noqa


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))

run docker-compose run --rm app sh -c "python manage.py test"

Add wait_for_db command and migrate command to docker-compose.

command: >
      sh -c "python manage.py wait_for_db &&
             python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"

run docker-compose down, docker-compose up

In checks.yml add python manage.py wait_for_db && before python manage.py test

commit and push