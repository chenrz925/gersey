from typing import Callable, MutableMapping, Text, Type

from taskflow.atom import Atom


class Geyser(object):
    atom_classes: MutableMapping[Text, Type[Atom]]

    @classmethod
    def atom(cls) -> Callable[[Type[Atom]], Type[Atom]]:
        def wrapper(atom: Type[Atom]) -> Type[Atom]:
            reference = f'{atom.__module__}.{atom.__name__}'
            cls.atoms[reference] = atom
            return atom

        return wrapper
    #
    # @classmethod
    # def
