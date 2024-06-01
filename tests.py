import sys

import cobble


def assert_equal(left, right):
    assert left == right


@cobble.data
class Album(object):
    name = cobble.field()
    year = cobble.field()


def test_module_of_class_is_module_of_caller():
    assert_equal("tests", Album.__module__)


def test_can_instantiate_empty_data_class():
    @cobble.data
    class Empty(object):
        pass

    Empty()


def test_can_instantiate_data_class_with_positional_arguments():
    album = Album("Everything in Transit", 2005)
    assert_equal("Everything in Transit", album.name)
    assert_equal(2005, album.year)


def test_can_instantiate_data_class_with_keyword_arguments():
    album = Album(name="Everything in Transit", year=2005)
    assert_equal("Everything in Transit", album.name)
    assert_equal(2005, album.year)


def test_init_calls_super_init():
    class Node(object):
        def __init__(self):
            self.is_node = True

    @cobble.data
    class Literal(Node):
        value = cobble.field()

    literal = Literal(42)
    assert_equal(True, literal.is_node)
    assert_equal(42, literal.value)


def test_repr_includes_class_name_and_field_values():
    album = Album(name="Everything in Transit", year=2005)
    assert_equal("Album(name='Everything in Transit', year=2005)", repr(album))


def test_str_is_the_same_as_repr():
    album = Album(name="Everything in Transit", year=2005)
    assert_equal(repr(album), str(album))


def test_equality_is_defined():
    @cobble.data
    class NotAnAlbum(object):
        name = cobble.field()
        year = cobble.field()

    album = Album(name="Everything in Transit", year=2005)
    assert(album == Album(name="Everything in Transit", year=2005))
    assert not (album == Album(name="Everything in Transit", year=2008))
    assert not (album == Album(name="The Glass Passenger", year=2005))
    assert not (album == Album(name="The Glass Passenger", year=2008))
    assert not (album == NotAnAlbum(name="Everything in Transit", year=2005))


def test_inequality_is_defined():
    @cobble.data
    class NotAnAlbum(object):
        name = cobble.field()
        year = cobble.field()

    album = Album(name="Everything in Transit", year=2005)
    assert not (album != Album(name="Everything in Transit", year=2005))
    assert (album != Album(name="Everything in Transit", year=2008))
    assert (album != Album(name="The Glass Passenger", year=2005))
    assert (album != Album(name="The Glass Passenger", year=2008))
    assert (album != NotAnAlbum(name="Everything in Transit", year=2005))


def test_hash_is_defined():
    def make_album():
        return Album(name="Everything in Transit", year=2005)
    # Hold references and assert twice to make sure we don't reuse the same object ID
    first_album = make_album()
    second_album = make_album()
    assert_equal(hash(first_album), hash(second_album))
    assert_equal(hash(first_album), hash(second_album))


def test_field_is_not_required_if_default_is_set_to_none():
    @cobble.data
    class Song(object):
        name = cobble.field()
        album = cobble.field(default=None)

    song = Song("MFEO")
    assert_equal(None, song.album)


def test_default_cannot_be_value_other_than_none():
    exception = _assert_raises(TypeError, lambda: cobble.field(default={}))
    assert_equal("default value must be None", str(exception))


def test_copy_updates_specified_attributes():
    base = Album(name="Everything in Transit", year=2004)
    album = cobble.copy(base, year=2005)
    assert_equal("Everything in Transit", album.name)
    assert_equal(2005, album.year)


class Expression(object):
    pass

@cobble.data
class Literal(Expression):
    value = cobble.field()

@cobble.data
class Add(Expression):
    left = cobble.field()
    right = cobble.field()

def test_visitor_abc_can_be_generated_from_visitable_subclass():
    class Evaluator(cobble.visitor(Expression)):
        def visit_literal(self, literal):
            return literal.value

        def visit_add(self, add):
            return self.visit(add.left) + self.visit(add.right)

    assert_equal(6, Evaluator().visit(Add(Literal(2), Literal(4))))

def test_visit_can_take_additional_argument():
    class Evaluator(cobble.visitor(Expression, args=1)):
        def visit_literal(self, literal, factor):
            return factor * literal.value

        def visit_add(self, add, factor):
            return self.visit(add.left, factor) + self.visit(add.right, factor)

    assert_equal(12, Evaluator().visit(Add(Literal(2), Literal(4)), 2))

def test_error_if_visitor_is_missing_methods():
    class Evaluator(cobble.visitor(Expression)):
        def visit_literal(self, literal):
            return literal.value

    error = _assert_raises(TypeError, Evaluator)

    if sys.version_info <= (3, 9):
        expected = "Can't instantiate abstract class Evaluator with abstract methods visit_add"
    else:
        expected = "Can't instantiate abstract class Evaluator with abstract method visit_add"
    assert_equal(expected, str(error))

def test_non_data_class_can_be_marked_as_visitable():
    class Expression(object):
        pass

    @cobble.visitable
    class Literal(Expression):
        def __init__(self, value):
            self.value = value

    class Evaluator(cobble.visitor(Expression)):
        def visit_literal(self, literal):
            return literal.value

    assert_equal(2, Evaluator().visit(Literal(2)))

def test_sub_sub_classes_are_included_in_abc():
    class Node(object):
        pass

    class Expression(Node):
        pass

    @cobble.data
    class Literal(Expression):
        value = cobble.field()

    class Evaluator(cobble.visitor(Node)):
        pass

    error = _assert_raises(TypeError, Evaluator)

    if sys.version_info <= (3, 9):
        expected = "Can't instantiate abstract class Evaluator with abstract methods visit_literal"
    else:
        expected = "Can't instantiate abstract class Evaluator with abstract method visit_literal"
    assert_equal(expected, str(error))


def _assert_raises(exception_type, func):
    try:
        func()
    except exception_type as error:
        return error

    assert False, "expected {0}".format(exception_type.__name__)
