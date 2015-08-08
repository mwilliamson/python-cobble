import cobble

from nose.tools import istest, assert_equal


@cobble.data
class Album(object):
    name = cobble.field()
    year = cobble.field()


@istest
def can_instantiate_data_class_with_positional_arguments():
    album = Album("Everything in Transit", 2005)
    assert_equal("Everything in Transit", album.name)
    assert_equal(2005, album.year)


@istest
def can_instantiate_data_class_with_keyword_arguments():
    album = Album(name="Everything in Transit", year=2005)
    assert_equal("Everything in Transit", album.name)
    assert_equal(2005, album.year)


@istest
def repr_includes_class_name_and_field_values():
    album = Album(name="Everything in Transit", year=2005)
    assert_equal("Album(name='Everything in Transit', year=2005)", repr(album))


@istest
def str_is_the_same_as_repr():
    album = Album(name="Everything in Transit", year=2005)
    assert_equal(repr(album), str(album))


@istest
def equality_is_defined():
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


@istest
def inequality_is_defined():
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


@istest
def field_is_not_required_if_default_is_set_to_none():
    @cobble.data
    class Song(object):
        name = cobble.field()
        album = cobble.field(default=None)
    
    song = Song("MFEO")
    assert_equal(None, song.album)


@istest
def default_cannot_be_value_other_than_none():
    exception = _assert_raises(TypeError, lambda: cobble.field(default={}))
    assert_equal("default value must be None", str(exception))


@cobble.visitable
class Expression(object):
    pass

@cobble.data
class Literal(Expression):
    value = cobble.field()

@cobble.data
class Add(Expression):
    left = cobble.field()
    right = cobble.field()

ExpressionVisitor = cobble.visitor(Expression)

@istest
def visitor_abc_can_be_generated_from_visitable_subclass():
    class Evaluator(ExpressionVisitor):
        def visit_literal(self, literal):
            return literal.value
        
        def visit_add(self, add):
            return self.visit(add.left) + self.visit(add.right)

    assert_equal(6, Evaluator().visit(Add(Literal(2), Literal(4))))


def _assert_raises(exception_type, func):
    try:
        func()
        assert False, "expected {0}".format(exception_type.__name__)
    except exception_type as error:
        return error
