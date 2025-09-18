from itertools import islice
from collections.abc import Iterable
from datetime import datetime


def make_session_id() -> str:
    return f"{datetime.now():%Y-%m-%d--%H-%M-%S}"


def chunked(items: Iterable, n) -> list:
    "behavior like in more_itertools.chunked"
    iterator = iter(items)
    res = []
    while chunk := list(islice(iterator, n)):
        res.append(chunk)
    return res
