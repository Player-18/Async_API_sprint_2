"""Gunicorn settings."""
import sys
import threading
import traceback

from gunicorn.arbiter import Arbiter
from uvicorn.workers import UvicornWorker

bind = "0.0.0.0:8080"
workers = 2

worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 100
timeout = 1000
keepalive = 2

spew = False

# Logging settings
errorlog = "-"
accesslog = "-"
loglevel = "info"
access_log_format = (
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
)


def post_fork(server: Arbiter, worker: UvicornWorker) -> None:
    """Хука, запускающаяся после создания воркера."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def pre_exec(server: Arbiter) -> None:
    """Хука, запускающаяся при пересоздании воркера."""
    server.log.info("Forked child, re-executing.")


def when_ready(server: Arbiter) -> None:
    """Хука, запускающаяся при полной готовности gunicorn."""
    server.log.info("Server is ready. Spawning workers")


def worker_int(worker: UvicornWorker) -> None:
    """Хука, запускающаяся при завершении работы воркера."""
    worker.log.info("worker received INT or QUIT signal")

    id2name = {th.ident: th.name for th in threading.enumerate()}
    code = []
    for thread_id, stack in sys._current_frames().items():
        thread_name = id2name.get(thread_id, "")
        code.append(f"\n# Thread: {thread_name}({thread_id})")
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append(f'File: "{filename}", line {lineno}, in {name}')
            if line:
                code.append(f"  {line.strip()}")
    worker.log.debug("\n".join(code))


def worker_abort(worker: UvicornWorker) -> None:
    """Хука, запускающаяся при завершении работы воркера сигналом ABRT."""
    worker.log.info("worker received SIGABRT signal")
