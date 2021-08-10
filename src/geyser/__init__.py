__version__ = '0.0.3'
__all__ = [
    'Geyser'
]

import argparse
from io import FileIO
from typing import Text, Callable
from pathlib import Path
from sys import path as sys_path

from _geysercpp import *


class Geyser:
    _core = Core()

    @classmethod
    def version(cls) -> Text:
        return __version__

    @classmethod
    def core_build(cls) -> Text:
        return cls._core.compiler

    @classmethod
    def _register_class(cls, name: Text, clazz: type, auto_compose: bool):
        name = clazz.__name__ if name is None else name
        if auto_compose:
            new_dict = {}
            new_dict.update(clazz.__dict__)
            new_dict['__init__'] = Composable.__dict__['__init__']
            clazz = type(name, (Composable,), new_dict)
        return cls._core.register_class(name, clazz)

    @classmethod
    def _build_executable(cls, name: Text, func: Callable):
        name = ''.join(map(
            lambda it: it.capitalize(),
            func.__name__.split('_'),
        )) if name is None else name
        clazz = type(name, (Composable,), {
            '__call__': func,
            '__module__': func.__module__,
            '__init__': Composable.__init__,
        })
        return clazz

    @classmethod
    def _parse_profile(cls, format, fp) -> dict:
        if format == 'json':
            import json
            return json.load(fp)
        elif format == 'yaml':
            from ruamel import yaml
            return yaml.load(fp)
        elif format == 'toml':
            import toml
            return toml.load(fp)
        else:
            raise ValueError('Unsupported format of profile')

    @classmethod
    def composable(cls, name: Text = None, auto_compose: bool = True, **kwargs):
        def wrapper(clz):
            cls._register_class(name, clz, auto_compose)
            return clz

        return wrapper

    @classmethod
    def executable(cls, name: Text = None, **kwargs):
        def wrapper(func):
            clz = cls._build_executable(name, func)
            cls._register_class(clz.__name__, clz, True)
            return clz

        return wrapper

    @classmethod
    def access(cls, reference: Text) -> type:
        return cls._core[reference]

    @classmethod
    def entry(cls):
        sys_path.append(str(Path('.').absolute()))
        parser = argparse.ArgumentParser(
            'geyser', description='Geyser: compose & execute python objects.'
        )
        parser.add_argument(
            'profile',
            nargs=1,
            type=argparse.FileType('r', encoding='utf8'),
            help='compose this profile'
        )
        parser.add_argument('-v', '--version', action='version', version=f'{__version__}')
        ns = parser.parse_args()
        if len(ns.profile) > 0:
            profile_file: FileIO = ns.profile[0]
            format_name = profile_file.readline().strip('\r\n #/')
            profile = cls._parse_profile(format_name, profile_file)
            compose = profile['__compose__']
            for key, value in compose.items():
                cls._core.compose(key, compose)
            execute = profile['__execute__']
            cls._core.execute(execute)


class Composable:
    def __init__(self, *args, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)


