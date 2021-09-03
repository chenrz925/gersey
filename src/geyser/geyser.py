from collections import OrderedDict
from inspect import isfunction
from logging import getLogger as get_logger, Logger
from typing import Callable, MutableMapping, Mapping, Text, Type, Any

from taskflow.atom import Atom
from taskflow.flow import Flow
from taskflow.patterns.graph_flow import Flow as GraphFLow, TargetedFlow
from taskflow.patterns.linear_flow import Flow as LinearFlow
from taskflow.patterns.unordered_flow import Flow as UnorderedFlow

from .context import Context
from .typedef import FunctorMeta, AtomMeta


class Geyser(object):
    atom_classes: MutableMapping[Text, AtomMeta] = OrderedDict()
    functors: MutableMapping[Text, FunctorMeta] = OrderedDict()
    flow_classes: Mapping[Text, Type[Flow]] = OrderedDict((
        ('linear', LinearFlow),
        ('unordered', UnorderedFlow),
        ('graph', GraphFLow),
        ('targeted_graph', TargetedFlow),
    ))

    logger: Logger = get_logger(f"geyser.geyser.Geyser")

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
                cls.atom_classes[reference] = AtomMeta(
                    atom=atom,
                    provides=provides,
                    requires=requires,
                    revert_requires=revert_requires
                )
            else:
                cls.logger.error(f'Type "{reference}" is NOT a subclass of taskflow.atom.Atom')
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
                cls.functors[reference] = FunctorMeta(
                    functor=functor,
                    provides=provides,
                    requires=requires,
                    revert_requires=revert_requires
                )
            else:
                cls.logger.error(f'Object "{reference}" is NOT a function')
            return functor

        return wrapper

    @classmethod
    def execute(cls, profile: Mapping[Text, Any]):
        context = Context(profile, cls.atom_classes, cls.functors, cls.flow_classes)
