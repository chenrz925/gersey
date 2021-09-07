__all__ = [
    'reflect',
    'inject_logger'
]

from importlib import import_module
from inspect import signature, Parameter
from logging import getLogger as get_logger
from typing import Text


def reflect(reference: Text) -> object:
    dot_splitted = reference.split('.')
    for idx in range(len(dot_splitted) - 1):
        module_ref = '.'.join(dot_splitted[:-(idx + 1)])
        try:
            module = import_module(module_ref)
            obj = module
            for name in dot_splitted[-(idx + 1):]:
                obj = getattr(obj, name)
            return obj
        except ImportError:
            continue
        except AttributeError:
            continue
    raise ImportError(f'Reference "{reference}" is invalid')


def inject_logger(type_, *args, **kwargs):
    sig = signature(type_)
    if 'logger' in kwargs:
        return type_(*args, **kwargs)
    elif 'logger' in sig.parameters or any(map(lambda it: it.kind == Parameter.VAR_KEYWORD, sig.parameters.values())):
        return type_(*args, logger=get_logger(f'{type_.__module__}.{type_.__name__}'), **kwargs)
    else:
        return type_(*args, **kwargs)
