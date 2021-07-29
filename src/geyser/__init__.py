__version__ = '0.0.1'
__all__ = [
    'Core', 'Geyser'
]

from typing import Text

from _geysercpp import *


class Geyser(object):
    _core = Core()

    @classmethod
    def _register_class(cls, clazz):
        pass

    @classmethod
    def register(cls, name: Text):
        def wrapper(clz):
            cls._register_class(clz)
            return clz

        return wrapper


def main():
    pass
