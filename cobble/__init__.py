import itertools
import functools

from .six import exec_, iteritems


def data(cls):
    fields = sorted(
        filter(
            None,
            map(functools.partial(_read_field, cls), dir(cls))
        ),
        key=lambda field: field[1].sort_key
    )
    stash = {}
    context = globals().copy()
    context[cls.__name__] = cls
    exec_("\n".join(_magic_methods(cls, fields)), context, stash)
    for key, value in iteritems(stash):
        setattr(cls, key, value)
    
    return cls

def _magic_methods(cls, fields):
    names = [name for name, field in fields]
    return [
        _make_init(fields),
        _make_repr(cls, names),
        _make_eq(cls, names),
        _make_neq(),
    ]


def _make_init(fields):
    def make_arg(name, field):
        if field.default == _undefined:
            return name
        else:
            return "{0}={1}".format(name, field.default)
    
    args_source = ", ".join(make_arg(name, field) for name, field in fields)
    assignments_source = "".join(
        "\n    self.{0} = {0}".format(name)
        for name, field in fields
    )
    return "def __init__(self, {0}):{1}\n".format(args_source, assignments_source)


def _make_repr(cls, names):
    return "def __repr__(self):\n     return '{0}({1})'.format({2})\n".format(
        cls.__name__,
        ", ".join("{0}={{{1}}}".format(name, index) for index, name in enumerate(names)),
        ", ".join("repr(self.{0})".format(name) for name in names)
    )


def _make_eq(cls, names):
    return "def __eq__(self, other):\n    return isinstance(other, {0}) and {1}".format(
        cls.__name__,
        " and ".join("self.{0} == other.{0}".format(name) for name in names)
    )

def _make_neq():
    return "def __ne__(self, other): return not (self == other)"


_sort_key_count = itertools.count()
_undefined = object()


def field(default=_undefined):
    if default not in [_undefined, None]:
        raise TypeError("default value must be None")
    return _Field(next(_sort_key_count), default=default)


class _Field(object):
    def __init__(self, sort_key, default):
        self.sort_key = sort_key
        self.default = default


def _read_field(cls, name):
    member = getattr(cls, name)
    if isinstance(member, _Field):
        return name, member
    else:
        return None
