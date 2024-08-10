#!/usr/bin/env bash

#fastapi dev /srv/app/core/main.py
gunicorn -k uvicorn.workers.UvicornWorker core.main:app --bind 0.0.0.0:8080