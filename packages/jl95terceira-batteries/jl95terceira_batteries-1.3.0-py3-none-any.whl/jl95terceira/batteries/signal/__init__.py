from signal import *

import abc       as _abc
import threading as _threading
import typing    as _typing
import uuid      as _uuid

_SIGINT_HOOKS:dict[str, _typing.Callable[[],None]] = dict()
_SIGINT_HOOKS_LOCK = _threading.Lock()
def _SIGINT_MASTER_HANDLER(*aa, **kaa):

    with _SIGINT_HOOKS_LOCK:
        
        for hook in _SIGINT_HOOKS.values(): 
            
            hook()

signal(SIGINT, _SIGINT_MASTER_HANDLER)

class HookHandler(_abc.ABC):

    def __init__(self, key:str): self._key = key

    @_typing.override
    def remove(self):
        
        with _SIGINT_HOOKS_LOCK:

            del _SIGINT_HOOKS[self._key]

def add_sigint_hook(hook:_typing.Callable[[],None]):

    with _SIGINT_HOOKS_LOCK:

        key                = _uuid.uuid4()
        _SIGINT_HOOKS[key] = hook
        return HookHandler(key)
