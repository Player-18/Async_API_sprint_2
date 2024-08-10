import time

from tests.functional.settings import Settings
from redis import Redis

settings = Settings()


if __name__ == '__main__':
    redis_client = Redis(host=settings.redis_host, port=settings.redis_port)
    while True:
        if redis_client.ping():
            break
        time.sleep(1)
