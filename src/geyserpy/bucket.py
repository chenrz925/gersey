from inspect import signature, Parameter
from typing import Text

from geyser import Logger


def replace_safe_init(init):
    def wrapper(self, **kwargs):
        self.__logger__ = Logger.get(f'{self.__class__.__module__}.{self.__class__.__name__}')

        in_args = kwargs.pop('__args__') if '__args__' in kwargs else []
        params = signature(init).parameters
        args_slot = None

        missing = []
        undefined = []

        for key, param in params.items():
            if param.kind == Parameter.POSITIONAL_OR_KEYWORD or param.kind == Parameter.KEYWORD_ONLY:
                if param.name not in kwargs and param.name is Parameter.empty:
                    missing.append(param)
            elif param.kind == Parameter.POSITIONAL_ONLY:
                if args_slot is None:
                    args_slot = []
                args_slot.append(param)
            elif param.kind == Parameter.VAR_POSITIONAL:
                args_slot = param

        for key, value in kwargs.items():
            if key not in params.keys():
                undefined.append(key)

        for key, value in params.items():
            if value.kind == Parameter.VAR_KEYWORD:
                undefined.clear()

        fill_args, fill_kwargs = [], {}

        if isinstance(args_slot, list) and len(args_slot) != len(in_args):
            raise ValueError(f'{len(args_slot)} argument(s) are/is needed, input {len(in_args)} argument(s)')
        else:
            fill_args.extend(in_args)

        if len(missing) > 0:
            missing_names = list(map(
                lambda param: param.name,
                missing
            ))
            raise ValueError(f'Argument(s) named {", ".join(missing_names)} is/are missing')
        if len(undefined) > 0:
            fill_kwargs.update(filter(
                lambda it: it[0] not in undefined,
                kwargs.items()
            ))
        else:
            fill_kwargs.update(kwargs.items())
        init(self, *fill_args, **fill_kwargs)

    return wrapper


def replace_auto_init(init):
    def wrapper(self, **kwargs):
        self.__logger__ = Logger.get(f'{self.__class__.__module__}.{self.__class__.__name__}')

        for key, item in kwargs.items():
            setattr(self, key, item)

    return wrapper


class Bucket:
    __raw__ = None
    __logger__ = Logger.get(f'geyser.Bucket')

    @property
    def logger(self):
        return self.__logger__

    def __init__(self, *args, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __mod__(self, item) -> bool:
        if isinstance(item, (tuple, list)):
            exists = True
            for it in item:
                exists = exists and hasattr(self, it)
            return exists
        else:
            return hasattr(self, item)

    def __bool__(self) -> bool:
        return hasattr(self, '__call__')

    def __invert__(self):
        if hasattr(self, '__return__'):
            return self.__return__
        else:
            raise NotImplementedError("No returned object.")

    @classmethod
    def raw(cls):
        return cls.__raw__

    @classmethod
    def create(cls, clazz: type, name: Text, auto_compose: bool, safe_compose: bool):
        if isinstance(clazz, type):
            if safe_compose:
                init = replace_safe_init(clazz.__init__)
            elif auto_compose:
                init = replace_auto_init(clazz.__init__)
            else:
                init = clazz.__init__
            return type(clazz.__name__ if name is not None else name, (clazz, Bucket), {
                "__raw__": clazz,
                "__module__": clazz.__module__,
                "__init__": init
            })
        else:
            return type(clazz.__name__, (Bucket,), {
                "__raw__": clazz,
                "__module__": clazz.__module__,
                "__init__": replace_auto_init(None),
                "__call__": clazz
            })
