from collections import namedtuple

FunctorMeta = namedtuple("FunctorMeta", ('functor', 'provides', 'requires', 'revert_requires'))
AtomMeta = namedtuple("AtomMeta", ('atom', 'provides', 'requires', 'revert_requires'))
