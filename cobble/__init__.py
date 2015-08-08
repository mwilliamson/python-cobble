import itertools
import functools

from .six import exec_, iteritems
from .inflection import underscore


def data(cls):
    fields = sorted(
        filter(
            None,
            map(functools.partial(_read_field, cls), dir(cls))
        ),
        key=lambda field: field[1].sort_key
    )
    definitions = _compile_definitions(_methods(cls, fields), {cls.__name__: cls})
    for key, value in iteritems(definitions):
        setattr(cls, key, value)
    
    return cls

def _methods(cls, fields):
    names = [name for name, field in fields]
    return [
        _make_init(fields),
        _make_repr(cls, names),
        _make_eq(cls, names),
        _make_neq(),
        _make_accept(cls),
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


def _make_accept(cls):
    return "def _accept(self, visitor): return visitor.visit_{0}(self)".format(underscore(cls.__name__))


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


def visitable(cls):
    return cls
    

def visitor(cls):
    source = """
class {0}Visitor(object):
    def visit(self, value):
        return value._accept(self)
""".format(cls.__name__)
    definition = _compile_definitions([source], {})
    return definition.values()[0]


def _compile_definitions(definitions, bindings):
    definition_globals = globals()
    definition_globals.update(bindings)
    stash = {}
    exec_("\n".join(definitions), definition_globals, stash)
    return stash
