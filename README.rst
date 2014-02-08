yaswfp
======

Yet Another SWF Parser.

You can pronounce whatever you like :)


How to use it
-------------

You can use ``swfparser.py`` as command line program or as a module.

If you execute directly the usage is::

    swfparser.py [-h] [-t] [-e] filepath

    positional arguments:
      filepath         the SWF file to parse

    optional arguments:
      -h, --help       show this help message and exit
      -t, --show-tags  show the first level tags of the file
      -e, --extended   show all objects with full detail and nested

If you want to use it as a module, you can use the ``SWFParser`` class
directly or the handy ``parsefile`` function::

    >>> swf = swfparser.parsefile(<yourSWFfile>)
    >>> swf.header
    Header(name=Header, FileLength=4228, ...)
    >>> len(swf.tags)
    365
    >>> swf.tags[0]
    UnknownObject(name=SetBackgroundColor, raw_payload=b'\xff\xff\xff')
    >>> swf.tags[3]
    >>> obj = swf.tags[3]
    >>> obj
    PlaceObject2(name=PlaceObject2, CharacterId=1, ...)
    >>> obj.CharacterId
    1
    >>> obj.Matrix.ScaleX
    65536


How to deal with still-unknown-objects
--------------------------------------

Not all the spec is covered (this is a work in progress!).

When the parser finds a structure that still can't process (because more
programming is needed), will just return an UnknownObject object with
the unparsed bytes, or will raise an exception if you set
the unknown_alert flag::

    SWFParser.unknown_alert = True

Add new structures to the parser is very simple. I'll be very glad to
do it if you offer a real stream of bytes as an example or even
a sample SWF file with the still missing object inside.


Development
-----------

To run the tests:

    ./test

You'll need ``python3-flake8`` and ``python3-nose``. Of course, this is
Python 3.

To complete some methods or be able to parse new structures, we should add
examples that show that new stuff, see current "sanity" tests. Yes, unit tests
are desirable, feel free to add those too.


Contact
-------

Any doubt, any question, any suggestion, or whatever, feel free to open
an issue here or find me in IRC, I'm ``facundobatista`` in Freenode.

Thanks!
