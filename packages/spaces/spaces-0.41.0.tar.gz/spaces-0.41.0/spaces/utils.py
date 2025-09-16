"""
"""
from __future__ import annotations

import base64
import ctypes
import json
import sys
from functools import lru_cache as cache
from functools import partial
from typing import Any

import multiprocessing
from multiprocessing.queues import SimpleQueue as _SimpleQueue
from pathlib import Path
from pickle import PicklingError
from typing import Callable
from typing import TypeVar

from .config import Config


GRADIO_VERSION_ERROR_MESSAGE = "Make sure Gradio version is at least 3.46"


T = TypeVar('T')


@cache
def self_cgroup_device_path() -> str:
    cgroup_content = Path(Config.zerogpu_proc_self_cgroup_path).read_text()
    for line in cgroup_content.strip().split('\n'):
        contents = line.split(':devices:')
        if len(contents) != 2:
            continue # pragma: no cover
        return contents[1]
    raise Exception # pragma: no cover


if sys.version_info.minor < 9: # pragma: no cover
    _SimpleQueue.__class_getitem__ = classmethod(lambda cls, _: cls) # type: ignore

class SimpleQueue(_SimpleQueue[T]):
    def __init__(self, *args):
        super().__init__(*args, ctx=multiprocessing.get_context('fork'))
    def put(self, obj: T):
        try:
            super().put(obj)
        except PicklingError:
            raise # pragma: no cover
        # https://bugs.python.org/issue29187
        except Exception as e:
            message = str(e)
            if not "pickle" in message:
                raise # pragma: no cover
            raise PicklingError(message)
    def close(self): # Python 3.8 static typing trick
        super().close() # type: ignore
    def wlock_release(self):
        if (lock := getattr(self, '_wlock', None)) is None:
            return # pragma: no cover
        try:
            lock.release()
        except ValueError:
            pass


def drop_params(fn: Callable[[], T]) -> Callable[..., T]:
    def drop(*args):
        return fn()
    return drop


def gradio_request_var():
    try:
        from gradio.context import LocalContext
    except ImportError: # pragma: no cover
        raise RuntimeError(GRADIO_VERSION_ERROR_MESSAGE)
    return LocalContext.request


def malloc_trim():
    ctypes.CDLL("libc.so.6").malloc_trim(0)


debug = partial(print, 'SPACES_ZERO_GPU_DEBUG')


def jwt_payload(token: str) -> dict[str, Any]:
    _, payload, _ = token.split('.')
    return json.loads(base64.urlsafe_b64decode(f'{payload}=='))
