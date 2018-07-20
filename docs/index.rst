.. currentmodule:: apng

pyAPNG API reference
====================

A Python module to deal with APNG file.

Usage/examples can be founded at `pyAPNG's readme <https://github.com/eight04/pyAPNG>`_.

Functions
---------

.. autofunction:: parse_chunks

.. autofunction:: make_chunk

.. autofunction:: make_text_chunk

Classes
-------

.. autoclass:: Chunk

.. autoclass:: PNG
  :members: open, open_any, from_bytes, to_bytes, save
  
  .. autoinstanceattribute:: chunks
    :annotation: = []

.. autoclass:: FrameControl
  :members: from_bytes, to_bytes

.. autoclass:: APNG
  :members: open, append, append_file, from_bytes, to_bytes, from_files, save
