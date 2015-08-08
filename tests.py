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
