.. currentmodule:: apng

pyAPNG API reference
====================

A Python module to deal with APNG file.

Usage/examples can be founded at `pyAPNG's readme <https://github.com/eight04/pyAPNG>`_.

Functions
---------

.. autofunction:: is_png

.. autofunction:: chunks

.. autofunction:: make_chunk

Classes
-------

.. autoclass:: PNG
   :members: open, from_chunks, to_bytes, save

.. autoclass:: FrameControl
   :members: to_bytes, from_bytes

.. autoclass:: APNG
   :members: append, to_bytes, from_files, open, save
