import itertools
import functools

from .six import exec_, iteritems


def data(cls):
    fields = sorted(
        filter(
            None,
            map(functools.partial(_read_field, cls), dir(cls))
        ),
        key=lambda field: field[1]._sort_key
    )
    stash = {}
    exec_("\n".join(_magic_methods(cls, fields)), globals(), stash)
    for key, value in iteritems(stash):
        setattr(cls, key, value)
    
    return cls

def _magic_methods(cls, fields):
    return [
        _make_init(fields),
        _make_repr(cls, fields),
    ]


def _make_init(fields):
    names = [name for name, field in fields]
    assignments_source = "".join(
        "\n    self.{0} = {0}".format(name)
        for name in names
    )
    return "def __init__(self, {0}):{1}\n".format(", ".join(names), assignments_source)


def _make_repr(cls, fields):
    names = [name for name, field in fields]
    return "def __repr__(self):\n     return '{0}({1})'.format({2})\n".format(
        cls.__name__,
        ", ".join("{0}={{{1}}}".format(name, index) for index, name in enumerate(names)),
        ", ".join("repr(self.{0})".format(name) for name in names)
    )

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
