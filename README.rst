Cobble
======

Cobble is a Python library that allows easy creation of data objects,
including implementations of common methods such as `__eq__` and `__repr__`.

Example
-------

.. code-block:: python

    import cobble

    @cobble.data
    class Song(object):
        name = cobble.field()
        artist = cobble.field()
        album = cobble.field(default=None)


    song = Song("MFEO", artist="Jack's Mannequin")

    print(song) # Prints "Song(name='MFEO', artist="Jack's Mannequin", album=None)"

License
-------

`2-Clause BSD <http://opensource.org/licenses/BSD-2-Clause>`_
