from dataclasses import dataclass


@dataclass
class Response:
    body: dict
    headers: dict
    status: int
