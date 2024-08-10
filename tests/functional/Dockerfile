FROM python:3.8-slim-buster

WORKDIR /tests/functional

COPY start.sh ./
COPY poetry.lock pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install

COPY . .

ENV PYTHONPATH "${PYTHONPATH}:/"

CMD ["/bin/bash", "start.sh"]
