import itertools
import functools

from .six import exec_


def data(cls):
    fields = sorted(
        filter(
            None,
            map(functools.partial(_read_field, cls), dir(cls))
        ),
        key=lambda field: field[1]._sort_key
    )
    names = [name for name, field in fields]
    assignments_source = "".join(
        "\n    self.{0} = {0}".format(name)
        for name in names
    )
    init_source = "def __init__(self, {0}):{1}".format(", ".join(names), assignments_source)
    repr_source = "def __repr__(self):\n     return '{0}({1})'.format({2})".format(
        cls.__name__,
        ", ".join("{0}={{{1}}}".format(name, index) for index, name in enumerate(names)),
        ", ".join("repr(self.{0})".format(name) for name in names)
    )
    stash = {}
    exec_(init_source, globals(), stash)
    exec_(repr_source, globals(), stash)
    cls.__init__ = stash["__init__"]
    cls.__repr__ = stash["__repr__"]
    
    return cls


_sort_key_count = itertools.count()


def field():
    return _Field(next(_sort_key_count))


class _Field(object):
    def __init__(self, sort_key):
        self._sort_key = sort_key


def _read_field(cls, name):
    member = getattr(cls, name)
    if isinstance(member, _Field):
        return name, member
    else:
        return None
