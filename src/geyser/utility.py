__all__ = [

]

from importlib import import_module
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
