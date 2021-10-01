__all__ = [
    'reflect',
    'inject_logger'
]

from importlib import import_module
from inspect import signature, Parameter
from logging import getLogger as get_logger
from typing import Text


def reflect(reference: Text) -> object:
    """
    # 反射器

    Args:
        reference (Text): 定义需要反射的对象路径

    Raises:
        ImportError: 当对应路径的对象不存在时，会触发该异常。

    Returns:
        object: 反射到的对象
    """
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
    """
    # 日志记录器注入

    当函数或类构造函数包含名为`logger`的形参时，注入一个名称为该类构造或函数路径的[日志记录器][logging.Logger]。

    首个参数必须为该类构造或函数，之后为调用调用该类构造或函数的参数。

    Args:
        type_ ([type]): [description]

    Returns:
        [type]: [description]
    """
    sig = signature(type_)
    if 'logger' in kwargs:
        return type_(*args, **kwargs)
    elif 'logger' in sig.parameters or any(map(lambda it: it.kind == Parameter.VAR_KEYWORD, sig.parameters.values())):
        try:
            return type_(*args, logger=get_logger(f'{type_.__module__}.{type_.__name__}'), **kwargs)
        except TypeError:
            return type_(*args, **kwargs)
    else:
        return type_(*args, **kwargs)

def reference(obj) -> Text:
    """
    # 对象路径获取

    获取某个对象路径的工具函数，当不确定某个任务或函数的实际路径时可通过该函数获取。

    Args:
        obj ([type]): 需要获取路径的对象

    Returns:
        Text: 该对象的路径
    """
    return f'{obj.__module__}.{obj.__name__}'
