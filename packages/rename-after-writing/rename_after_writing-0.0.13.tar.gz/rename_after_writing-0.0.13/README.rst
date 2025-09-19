####################
rename_after_writing
####################
|TestStatus| |PyPiStatus| |BlackStyle| |BlackPackStyle| |MITLicenseBadge|

A python-library to help with the completeness of files when moving, copying and writing.
Writing a file is not atomic. In the worst case the process writing the file
dies while the file is not yet complete.
Also in some network-file-systems, the destination of a ``move`` or ``copy`` might show up before it is complete.
Incomplete files are a potential risk for the integrity of your data.
In the best case your reading process crashes, but in the worst case the incompleteness goes unnoticed.
This package reduces the risk of having incomplete files by making all writing
operations write to a temporary file in the destination's directory first before renaming it to its final destination.
On most file-systems this final renamig is atomic.


*******
Install
*******

.. code-block::

    pip install rename_after_writing


*********
Functions
*********


Path
====

Writes to a temporary path and move it to your desired ``path`` on exit.

.. code-block:: python

    import rename_after_writing as rnw

    with rnw.Path(path="my_file.txt") as tmp_path:
        with open(tmp_path, "wt") as f:
            for i in range(10):
                f.write(input())

Note, that while you write to the file (while you provide ``input()``) the
file is written into a temporary file named ``path`` + ``.`` + ``uuid()``.
After writing, on exit of the contextmanager, the temporary file is moved to
``path``.

open
====

Just like python's built in ``open()`` but when writing (``mode=w``) everything is writen
to a temporary file in the destination's directory before the temporary file is renamed to the final destination.

.. code-block:: python

    import rename_after_writing as rnw

    with rnw.open("my_file.txt", "wt") as f:
        for i in range(10):
            f.write(input())


copy
====

Copies the file first to a temporary file in the destinations directory
before moving it to its final path.


.. code-block:: python

    import rename_after_writing as rnw

    rnw.copy(src="machine/with/src", dst="other/machine/in/network/dst")


move
====

Some implementations of network-file-systems might raise an
``OSError`` with ``errno.EXDEV`` when an ``os.rename()`` is going across the
boundary of a physical drive.
In this case, this package's ``copy`` is used to copy the file beore unlinking
the source-file.


.. code-block:: python

    import rename_after_writing as rnw

    rnw.move(src="machine/with/src", dst="other/machine/in/network/dst")


.. |BlackStyle| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |TestStatus| image:: https://github.com/cherenkov-plenoscope/rename_after_writing/actions/workflows/test.yml/badge.svg?branch=main
    :target: https://github.com/cherenkov-plenoscope/rename_after_writing/actions/workflows/test.yml

.. |PyPiStatus| image:: https://img.shields.io/pypi/v/rename_after_writing
    :target: https://pypi.org/project/rename_after_writing

.. |BlackPackStyle| image:: https://img.shields.io/badge/pack%20style-black-000000.svg
    :target: https://github.com/cherenkov-plenoscope/black_pack

.. |MITLicenseBadge| image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
