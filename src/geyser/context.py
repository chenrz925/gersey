from collections import OrderedDict
from copy import copy
from importlib import import_module
from json import loads
from pkgutil import get_data
from typing import Mapping, Text, Any, Type

from jsonschema import validate
from taskflow.atom import Atom
from taskflow.flow import Flow

from .typedef import FunctorMeta, AtomMeta


class Context(object):
    schema = loads(get_data(__package__, 'schema.json'))
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
        self.profile = profile
        validate(self.profile, self.schema)
        self.atom_classes = atom_classes
        self.functors = functors
        self.flow_classes = flow_classes
        self.atoms = OrderedDict()
        self.flows = OrderedDict()

    def _parse_module(self, reference: Text) -> Text:
        return '.'.join(reference.split('.')[:-1])

    def _access_atom_class(self, reference: Text) -> AtomMeta:
        if reference in self.atom_classes:
            return self.atom_classes[reference]
        else:
            import_module(self._parse_module(reference))
            return self.atom_classes[reference]

    def _access_functor(self, reference: Text) -> FunctorMeta:
        if reference in self.functors:
            return self.atom_classes[reference]
        else:
            import_module(self._parse_module(reference))
            return self.functors[reference]

    def _build_atom(self, profile: Mapping[Text, Text]) -> Atom:
        reference: Text = profile['reference']
        name: Text = profile['name']
        inject: Mapping[Text, Text] = profile['inject'] if 'inject' in profile else {}
        rebind: Mapping[Text, Text] = profile['rebind'] if 'rebind' in profile else {}
        revert_rebind: Mapping[Text, Text] = profile['revert_rebind'] if 'revert_rebind' in profile else {}

        meta = self._access_atom_class(reference)
        return meta.atom(
            name=name, provides=meta.provides, requires=meta.requires,
            rebind=rebind, inject=inject, revert_rebind=revert_rebind,
            revert_requires=meta.revert_requires
        )
