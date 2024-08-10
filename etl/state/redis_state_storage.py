import abc
from typing import Any, Dict

from redis import Redis


class BaseStorage(abc.ABC):
    """Abstract storage"""

    @abc.abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        """Save state to storage"""

    @abc.abstractmethod
    def retrieve_state(self) -> Dict[str, Any]:
        """Retrieve state from storage"""


class RedisStorage(BaseStorage):

    def __init__(self, redis_adapter: Redis):
        self.redis_adapter = redis_adapter

    def save_state(self, state: Dict[str, Any]) -> None:
        """Save state to storage"""
        self.redis_adapter.hset("data", mapping=state)

    def retrieve_state(self) -> Dict[str, Any]:
        """Retrieve state from storage"""
        return self.redis_adapter.hgetall('data')


class State:
    """Class for working with state"""

    def __init__(self, storage: RedisStorage) -> None:
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Set state for key"""
        self.storage.save_state({key: value})

    def get_state(self, key: str) -> Any:
        """Get state by key"""
        state = self.storage.retrieve_state()
        return state.get(key)

