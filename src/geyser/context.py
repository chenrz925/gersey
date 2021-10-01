from collections import OrderedDict
from copy import copy
from importlib import import_module
from json import loads
from logging import getLogger as get_logger
from pkgutil import get_data
from typing import Mapping, Text, Any, Type, Sequence, List, MutableMapping, Union

from jsonschema import validate
from taskflow import engines
from taskflow.atom import Atom
from taskflow.engines.base import Engine
from taskflow.flow import Flow
from taskflow.persistence import backends
from taskflow.task import FunctorTask, ReduceFunctorTask, MapFunctorTask
from ruamel.yaml import dump

from .typedef import FunctorMeta, AtomMeta


class Context(object):
    _schema = loads(get_data(__package__, 'schema.json'))
    _init_globals = copy(globals())
    _ptr_globals = globals()

    def __init__(
            self, profile: Mapping[Text, Any],
            atom_classes: Mapping[Text, AtomMeta],
            functors: Mapping[Text, FunctorMeta],
            flow_classes: Mapping[Text, Type[Flow]]
    ):
        self._ptr_globals.clear()
        self._ptr_globals.update(self._init_globals)
        self._profile = profile
        validate(self._profile, self._schema)
        self._atom_classes = atom_classes
        self._functors = functors
        self._flow_classes = flow_classes
        self._atoms = OrderedDict()
        self._root_flow = None
        self._engine = None
        self._logger = get_logger(
            f'{self.__class__.__module__}.{self.__class__.__name__}')
        self.inject_atoms(self._profile['tasks']
                          if 'tasks' in self._profile else [])
        self.inject_flow(self._profile['flow']
                         if 'flow' in self._profile else {})
        self.inject_engine()

    def _parse_module(self, reference: Text) -> Text:
        return '.'.join(reference.split('.')[:-1])

    def _access_atom_class(self, reference: Text) -> AtomMeta:
        if reference in self._atom_classes:
            return self._atom_classes[reference]
        else:
            import_module(self._parse_module(reference))
            return self._atom_classes[reference]

    def _access_functor(self, reference: Text) -> FunctorMeta:
        if reference in self._functors:
            return self._functors[reference]
        else:
            import_module(self._parse_module(reference))
            return self._functors[reference]

    def _rename_provide(self, provide: Sequence[Text], rename: Mapping[Text, Text]) -> Sequence[Text]:
        if isinstance(provide, set):
            return set(map(
                lambda it: rename[it] if it in rename else it,
                provide
            ))
        else:
            return list(map(
                lambda it: rename[it] if it in rename else it,
                provide
            ))

    def _build_atom(self, profile: MutableMapping[Text, Text]) -> Atom:
        reference: Text = profile['reference']
        name: Text = profile['name']
        inject: MutableMapping[Text,
                               Text] = profile['inject'] if 'inject' in profile else {}
        rebind: Mapping[Text,
                        Text] = profile['rebind'] if 'rebind' in profile else {}
        rename: Mapping[Text,
                        Text] = profile['rename'] if 'rename' in profile else {}
        revert_rebind: Mapping[Text,
                               Text] = profile['revert_rebind'] if 'revert_rebind' in profile else {}

        inject['logger'] = get_logger(reference)
        meta = self._access_atom_class(reference)
        return meta.atom(
            name=name, provides=self._rename_provide(meta.provides, rename), requires=meta.requires,
            rebind=rebind, inject=inject, revert_rebind=revert_rebind,
            revert_requires=meta.revert_requires
        )

    def _build_functor(self, profile: MutableMapping[Text, Text]) -> Atom:
        reference: Text = profile['reference']
        name: Text = profile['name']
        inject: Mapping[Text,
                        Text] = profile['inject'] if 'inject' in profile else {}
        rebind: Mapping[Text,
                        Text] = profile['rebind'] if 'rebind' in profile else {}
        rename: Mapping[Text,
                        Text] = profile['rename'] if 'rename' in profile else {}
        typename: Text = profile['type'] if 'type' in profile else "functor"

        inject['logger'] = get_logger(reference)
        meta = self._access_functor(reference)
        if typename == 'mapper':
            return MapFunctorTask(
                functor=meta.functor, name=name, provides=self._rename_provide(
                    meta.provides, rename),
                requires=meta.requires, rebind=rebind, inject=inject
            )
        elif typename == 'reducer':
            return ReduceFunctorTask(
                functor=meta.functor, name=name, provides=self._rename_provide(
                    meta.provides, rename),
                requires=meta.requires, rebind=rebind, inject=inject
            )
        else:
            return FunctorTask(
                execute=meta.functor, name=name, provides=self._rename_provide(
                    meta.provides, rename),
                requires=meta.requires, rebind=rebind, inject=inject
            )

    def _build(self, profile: Mapping[Text, Text]) -> Atom:
        typename: Text = profile['type'] if 'type' in profile else 'task'

        if typename == 'task':
            return self._build_atom(profile)
        else:
            return self._build_functor(profile)

    def inject_atoms(self, profile: Sequence[Mapping[Text, Any]]):
        self._atoms.clear()
        self._atoms.update(
            map(lambda it: (it['name'], self._build(it)), profile))

    def _build_flow(self, profile: Mapping[Text, Any]) -> Flow:
        name: Text = profile['name']
        typename: Text = profile['type']
        include: List[Union[Text, Mapping[Text, Any]]] = profile['include']

        flow = self._flow_classes[typename](name)
        for it in include:
            if isinstance(it, str):
                flow.add(self._atoms[it])
            else:
                flow.add(self._build_flow(it))
        return flow

    def inject_flow(self, profile: Mapping[Text, Any]):
        self._root_flow = self._build_flow(profile)

    def inject_engine(self):
        if 'backend' in self._profile:
            if 'executor' in self._profile:
                self._engine: Engine = engines.load(
                    self._root_flow,
                    engine=self._profile['engine'] if 'engine' in self._profile else 'serial',
                    backend=backends.fetch(conf=self._profile['backend']),
                    executor=self._profile['executor'] if 'executor' in self._profile else 'thread'
                )
            else:
                self._engine: Engine = engines.load(
                    self._root_flow,
                    engine=self._profile['engine'] if 'engine' in self._profile else 'serial',
                    backend=backends.fetch(conf=self._profile['backend'])
                )
        else:
            self._engine: Engine = engines.load(
                self._root_flow,
                engine=self._profile['engine'] if 'engine' in self._profile else 'serial'
            )
        self._engine.storage.inject(
            self._profile['inject'] if 'inject' in self._profile else {})
        self._engine.compile()
        self._logger.info(f'Finish compiling engine.')
        self._logger.info(
            f'Engine compilation:\n{self._engine.compilation.execution_graph.pformat()}')
        self._engine.prepare()
        self._logger.info('Finish preparing engine.')
        self._engine.validate()
        self._logger.info('Finish validating engine.')

    def __call__(self, *args, **kwargs):
        ret = self._engine.run()
        self._logger.info(
            f'Engine statistics:\n{dump(self._engine.statistics)}')
