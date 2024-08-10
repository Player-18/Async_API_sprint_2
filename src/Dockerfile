FROM python:3.10.7-slim-buster

RUN apt-get update && \
  apt-get install --no-install-recommends -y python-psycopg2 wget make wait-for-it\
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/app

COPY start.sh ./
COPY poetry.lock pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install

COPY . /srv/app

EXPOSE 8000

CMD ["/bin/bash", "start.sh"]
