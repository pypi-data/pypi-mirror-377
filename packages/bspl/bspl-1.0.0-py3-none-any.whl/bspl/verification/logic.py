"""
Logic operations for combining objects that represent named statements, to improve readability.

Named statements are represented as name/statement pairs in a dict.
Because conjunction is more common, it is represented my merging dicts.
Disjunction is represented by a list instead.

E.x.:
>>> a = Name(a, "A")
{"A": a}
>>> b = Name(b, "B")
{"B": b}
>>> And(a,b)
{"A": a, "B": b}
>>> Or(a,b)
[{"A":a}, {"B":b}]
"""

# TODO: Replace boolexpr with modern SAT solver (PySAT) for Python 3.11+ compatibility
try:
    import boolexpr as bx
    from boolexpr import *

    HAS_BOOLEXPR = True
except ImportError:
    HAS_BOOLEXPR = False

    # Provide minimal fallbacks for when boolexpr is not available
    class _BoolExprNotAvailable:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "boolexpr is required for SAT solving functionality. Install with: pip install bspl[sat]"
            )

    # Create placeholder objects that raise helpful errors
    Variable = _BoolExprNotAvailable
    not_ = _BoolExprNotAvailable
    and_ = _BoolExprNotAvailable
    or_ = _BoolExprNotAvailable
    onehot0 = _BoolExprNotAvailable
from itertools import combinations, permutations, chain
from ..utils import merge


def Name(statement, name):
    return {name: statement}


def And(*statements):
    o = {}
    for s in statements:
        o = merge(o, s)
    return o


def Or(*statements):
    return statements


def count(statements):
    if type(statements) is list or type(statements) is tuple:
        # disjunction
        return sum(count(s) for s in statements)
    elif type(statements) is dict:
        # conjunction
        return sum(count(s) for s in statements.values())
    else:
        # atomic statement
        return 1


def compile(statements):
    if type(statements) is list or type(statements) is tuple:
        # disjunction
        return or_s(*[compile(s) for s in statements])
    elif type(statements) is dict:
        # conjunction
        return and_s(*[compile(s) for s in statements.values()])
    else:
        # atomic statement
        return statements


def named(arg):
    def wrap(fn, name=arg):
        """Wrapper for functions that return logic statements, to track where
        they came from"""

        def wrapped(*args, **kwds):
            n = name or "-".join([a.name for a in args] + [fn.__name__])
            return Name(fn(*args, **kwds), n)

        return wrapped

    if type(arg) is str:
        return wrap
    else:
        return wrap(arg, None)
