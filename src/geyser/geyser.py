from collections import OrderedDict
from inspect import isfunction
from logging import getLogger as get_logger, Logger
from typing import Callable, MutableMapping, Mapping, Text, Type, Any
import json
import plistlib
from ruamel import yaml
import toml
import argparse
from os.path import abspath, exists, join as path_join, dirname

try:
    import pyhocon
except ModuleNotFoundError:
    pyhocon = None

from taskflow.atom import Atom
from taskflow.flow import Flow
from taskflow.patterns.graph_flow import Flow as GraphFLow, TargetedFlow
from taskflow.patterns.linear_flow import Flow as LinearFlow
from taskflow.patterns.unordered_flow import Flow as UnorderedFlow

from .context import Context
from .typedef import FunctorMeta, AtomMeta

__version__ = '0.3.0'


class Geyser(object):
    _atom_classes: MutableMapping[Text, AtomMeta] = OrderedDict()
    _functors: MutableMapping[Text, FunctorMeta] = OrderedDict()
    _flow_classes: Mapping[Text, Type[Flow]] = OrderedDict((
        ('linear', LinearFlow),
        ('unordered', UnorderedFlow),
        ('graph', GraphFLow),
        ('targeted_graph', TargetedFlow),
    ))

    _logger: Logger = get_logger(f"geyser.geyser.Geyser")

    @classmethod
    def task(
            cls,
            provides: Mapping[Text, Any] = (),
            requires: Mapping[Text, Any] = (),
            revert_requires: Mapping[Text, Any] = ()
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
            provides: Mapping[Text, Any] = (),
            requires: Mapping[Text, Any] = (),
            revert_requires: Mapping[Text, Any] = ()
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
    def _load_profile(cls, path: Text) -> Mapping[Text, Any]:
        suffix = path.split('.')[-1].lower()
        if exists(abspath(path)):
            path = abspath(path)
        else:
            try:
                import geyser_bucket
                path = abspath(path_join(dirname(geyser_bucket.__file__), path))
            except ModuleNotFoundError:
                pass
        return getattr(cls, f'_load_profile_{suffix}', cls._load_profile_)(path)

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
            return yaml.load(fp)

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
    def _set_proc_title(cls):
        try:
            from setproctitle import setproctitle
            setproctitle('geyser')
        except ModuleNotFoundError:
            return

    @classmethod
    def _build_parser(cls) -> argparse.ArgumentParser:
        cls._set_proc_title()
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
            'profiles',
            nargs='+',
        )
        return parser

    @classmethod
    def entry(cls):
        ns = cls._build_parser().parse_args()
        for profile in ns.profiles:
            context = cls._build_context(cls._load_profile(profile))
            context()
        return 0
