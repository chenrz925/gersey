import argparse
import json
import plistlib
import sys
from collections import OrderedDict
from inspect import isfunction
from logging import config as logging_config, getLogger as get_logger
from os import environ, system
from os.path import abspath
from pathlib import Path
from platform import python_version, python_compiler, python_build, platform, python_implementation
from sys import path as sys_path
from typing import Callable, MutableMapping, Mapping, Text, Type, Any, Sequence

from more_itertools import flatten

if sys.version_info < (3, 10):
    try:
        from importlib_metadata import entry_points
    except ModuleNotFoundError:
        from pkg_resources import iter_entry_points


        def entry_points(*args, **kwargs):
            return tuple(iter_entry_points(*args, **kwargs))
else:
    from importlib.metadata import entry_points

import pyhocon
import toml
from ruamel import yaml
from setproctitle import setproctitle
from taskflow.atom import Atom
from taskflow.flow import Flow
from taskflow.patterns.graph_flow import Flow as GraphFLow, TargetedFlow
from taskflow.patterns.linear_flow import Flow as LinearFlow
from taskflow.patterns.unordered_flow import Flow as UnorderedFlow

from .context import Context
from .typedef import FunctorMeta, AtomMeta

__version__ = '0.4.7'


class Geyser(object):
    _atom_classes: MutableMapping[Text, AtomMeta] = OrderedDict()
    _functors: MutableMapping[Text, FunctorMeta] = OrderedDict()
    _flow_classes: Mapping[Text, Type[Flow]] = OrderedDict((
        ('linear', LinearFlow),
        ('unordered', UnorderedFlow),
        ('graph', GraphFLow),
        ('targeted_graph', TargetedFlow),
    ))

    _logger = None

    @classmethod
    def task(
            cls,
            provides: Sequence[Text] = (),
            requires: Sequence[Text] = (),
            revert_requires: Sequence[Text] = ()
    ) -> Callable[[Type[Atom]], Type[Atom]]:
        def wrapper(atom: Type[Atom]) -> Type[Atom]:
            reference = f'{atom.__module__}.{atom.__name__}'
            if issubclass(atom, Atom):
                cls._atom_classes[reference] = AtomMeta(
                    atom=atom,
                    provides=provides,
                    requires=requires,
                    revert_requires=revert_requires
                )
            else:
                cls._logger.error(f'Type "{reference}" is NOT a subclass of taskflow.atom.Atom')
            return atom

        return wrapper

    @classmethod
    def functor(
            cls,
            provides: Sequence[Text] = (),
            requires: Sequence[Text] = (),
            revert_requires: Sequence[Text] = ()
    ) -> Callable[[Callable], Callable]:
        def wrapper(functor: Callable) -> Callable:
            reference = f'{functor.__module__}.{"".join(map(lambda it: it.capitalize(), functor.__name__.split("_")))}'
            if isfunction(functor):
                cls._functors[reference] = FunctorMeta(
                    functor=functor,
                    provides=provides,
                    requires=requires,
                    revert_requires=revert_requires
                )
            else:
                cls._logger.error(f'Object "{reference}" is NOT a function')
            return functor

        return wrapper

    @classmethod
    def _build_context(cls, profile: Mapping[Text, Any]):
        return Context(profile, cls._atom_classes, cls._functors, cls._flow_classes)

    @classmethod
    def _profile_search_paths(cls):
        return [
            Path('.').absolute(),
            *tuple(flatten(map(
                lambda it: it.profile_paths(),
                filter(
                    lambda it: hasattr(it, 'profile_paths'),
                    map(
                        lambda it: it.load(),
                        entry_points(group='geyser.profile')
                    )
                )
            )))
        ]

    @classmethod
    def _load_profile(cls, path: Text) -> Mapping[Text, Any]:
        for profile_root in cls._profile_search_paths():
            print(profile_root)
            profile_path = profile_root.joinpath(path)
            if profile_path.exists():
                suffix = path.split('.')[-1].lower()
                return getattr(cls, f'_load_profile_{suffix}', cls._load_profile_)(str(profile_path))

        raise FileNotFoundError(
            f'File {path} does NOT exist in ({", ".join(map(lambda it: str(it), cls._profile_search_paths()))})')

    @classmethod
    def _load_profile_(cls, path: Text) -> Mapping[Text, Any]:
        raise NotImplementedError(f'Format of profile "{path}" is not supported')

    @classmethod
    def _load_profile_json(cls, path: Text) -> Mapping[Text, Any]:
        with open(path, 'r') as fp:
            return json.load(fp)

    @classmethod
    def _load_profile_plist(cls, path: Text) -> Mapping[Text, Any]:
        with open(path, 'rb') as fp:
            return plistlib.load(fp)

    @classmethod
    def _load_profile_yaml(cls, path: Text) -> Mapping[Text, Any]:
        with open(path, 'r') as fp:
            return yaml.load(fp, Loader=yaml.Loader)

    @classmethod
    def _load_profile_yml(cls, path: Text) -> Mapping[Text, Any]:
        return cls._load_profile_yaml(path)

    @classmethod
    def _load_profile_toml(cls, path: Text) -> Mapping[Text, Any]:
        with open(path, 'r') as fp:
            return toml.load(fp)

    @classmethod
    def _load_profile_tml(cls, path: Text) -> Mapping[Text, Any]:
        return cls._load_profile_toml(path)

    @classmethod
    def _load_profile_hocon(cls, path: Text) -> Mapping[Text, Any]:
        if pyhocon:
            return pyhocon.ConfigFactory.parse_file(path)
        else:
            return cls._load_profile_(path)

    @classmethod
    def execute(cls, profile: Mapping[Text, Any]):
        context = cls._build_context(profile)
        return context()

    @classmethod
    def _build_parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            'geyser',
            description='Inject and execute tasks.'
        )
        parser.add_argument(
            '-v', '--version',
            action='version',
            version=f'%(prog)s {__version__}'
        )
        parser.add_argument(
            '-d', '--debug',
            action='store_true',
        )
        parser.add_argument(
            '-l', '--log',
            nargs='+'
        )
        parser.add_argument(
            '-q', '--quiet',
            action='store_true'
        )
        parser.add_argument(
            '-e', '--edit',
            action='store_true'
        )
        parser.add_argument(
            'profile',
            nargs='+',
        )
        return parser

    @classmethod
    def _setting_logging(cls, ns):
        handlers = {}
        if not ns.quiet and not ns.log:
            handlers['console'] = {
                'class': 'logging.StreamHandler',
                'formatter': 'colored',
                'level': 'DEBUG' if ns.debug else 'INFO',
                'stream': 'ext://sys.stdout',
            }
        else:
            sys.stdin.close()
            sys.stdin = open('/dev/null', 'r')
            sys.stdout.close()
            sys.stdout = open('/dev/null', 'r')
            sys.stderr.close()
            sys.stderr = open('/dev/null', 'w')
        handlers.update(map(lambda it: (f'file{it[0]}', {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'plain',
            'level': 'DEBUG',
            'when': 'D',
            'filename': it[1]
        }), enumerate(ns.log if ns.log else [])))
        logging_config.dictConfig({
            'version': 1,
            'formatters': {
                'colored': {
                    '()': 'colorlog.ColoredFormatter',
                    'format': "%(log_color)s(%(asctime)s)[%(levelname)s][%(process)d][%(thread)d][%(name)s]%(reset)s:"
                              " %(message)s",
                },
                'plain': {
                    '()': 'logging.Formatter',
                    'format': "(%(asctime)s)[%(levelname)s][%(process)d][%(thread)d][%(name)s]: %(message)s"
                }
            },
            'handlers': handlers,
            'root': {
                'level': 'NOTSET',
                'handlers': list(handlers.keys())
            }
        })
        cls._logger = get_logger(f'{cls.__module__}.{cls.__name__}')

    @classmethod
    def _setting_module_path(cls):
        sys_path.append(abspath('.'))
        path_file = Path.home() / '.geyser' / 'PYTHONPATH'
        if path_file.exists():
            with path_file.open('r') as fp:
                for path in fp.readlines():
                    sys_path.append(path.strip())

    @classmethod
    def _call_editor(cls, ns):
        editor_file = Path.home() / '.geyser' / 'EDITOR'
        if 'EDITOR' in environ:
            editor = environ['EDITOR']
        elif editor_file.exists():
            editor = editor_file.open('r').readline().strip()
        else:
            editor = 'vi'
        for profile in ns.profile:
            system(f'{editor} {profile}')

    @classmethod
    def entry(cls):
        ns = cls._build_parser().parse_args()
        cls._setting_module_path()
        cls._setting_logging(ns)
        cls._logger.info(f'Geyser {__version__}')
        cls._logger.info(
            f'Python ({python_implementation()}) {python_version()} {python_compiler()} {python_build()[1]}')
        cls._logger.info(f'OS {platform()}')
        if ns.edit:
            cls._call_editor(ns)
        else:
            for profile in ns.profile:
                setproctitle(f'geyser {profile}')
                context = cls._build_context(cls._load_profile(profile))
                context()
        return 0
