FROM python:3.8
LABEL maintainer="u6k.apps@gmail.com"

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    pip install pipenv

WORKDIR /var/myapp
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install

VOLUME /var/myapp

CMD ["pipenv", "run", "celery"]
