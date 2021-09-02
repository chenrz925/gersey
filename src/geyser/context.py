from collections import OrderedDict
from taskflow.atom import Atom

class Context(object):
    class AtomContext(OrderedDict):
        def __setitem__(self, key, value):
            assert isinstance(value, Atom)
