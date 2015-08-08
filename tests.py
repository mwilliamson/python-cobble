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
