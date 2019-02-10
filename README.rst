pyAPNG
======

.. image:: https://travis-ci.org/eight04/pyAPNG.svg?branch=master
  :target: https://travis-ci.org/eight04/pyAPNG
  
.. image:: https://readthedocs.org/projects/pyapng/badge/?version=latest
  :target: http://pyapng.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

A Python module to deal with APNG file.

Features
--------

- Merge multiple images into one APNG file. (It use Pillow to convert images into PNG format)
- Read APNG file and extract each frames into PNG file.
- It doesn't do any optimization but only concat the images. This might be changed in the future.

Dependencies
------------

- `Pillow <https://github.com/python-pillow/Pillow>`__ - **Optional**. You can still use pyAPNG without PIL but it can only read PNG files.

Development dependencies
------------------------

- `pngcheck <http://www.libpng.org/pub/png/apps/pngcheck.html>`_
- See requirements.txt for other dev-dependencies.

Installation
------------

From `pypi <https://pypi.org/project/apng/>`__::

  pip install apng

Usage
-----

Convert a series of images into APNG animation:

.. code:: python

  from apng import APNG
    
  APNG.from_files(["1.jpg", "2.jpg", "3.jpg"], delay=100).save("result.png")
    
Use different delays:

.. code:: python

  from apng import APNG
    
  files = [
    ("1.jpg", 100),
    ("2.jpg", 200),
    ("3.jpg", 300)
  ]
    
  im = APNG()
  for file, delay in files:
    im.append_file(file, delay=delay)
  im.save("result.png")

Extract frames from an APNG file:
    
.. code:: python

  from apng import APNG
    
  im = APNG.open("animation.png")
  for i, (png, control) in enumerate(im.frames):
    png.save("{i}.png".format(i=i))
    
Add a text chunk to the PNG file:

.. code:: python

  from apng import PNG, make_text_chunk
  
  im = PNG.open("image.png")
  im.chunks.append(make_text_chunk(key="Comment", value="Some text"))
  im.save("image.png")
    
Performance
-----------

If you want to convert some large JPGs into animation, the library has to convert your JPGs into PNGs then merge them into a single animation APNG file. The problems are:

1. It is extremely slow.
2. The file size of the APNG is extremely large. Probably 5x of the original or more.

In this case, I suggest trying an animation format called "ugoira", which is implemented by Pixiv.net. There is also an image viewer named "HoneyView" which can view it locally.
        
Document
---------

http://pyapng.readthedocs.io/en/latest/

Todos
-----

- Add optimizer?

Changelog
---------

- 0.3.3 (Feb 11, 2019)

  - Fix: failed to extract frames containing multiple ``fdAT`` chunks.

- 0.3.2 (Jul 20, 2018)

  - Add: ``make_text_chunk`` function.
  - Add: ``Chunk`` data class.
  - Change: now ``parse_chunks`` yields ``Chunk`` instead of a tuple. This should be safe since ``Chunk`` is a namedtuple.

- 0.3.1 (May 13, 2018)

  - Add: universal wheel.

- 0.3.0 (May 13, 2018)

  - Support Python 2.
  - Add: PNG method ``open_any``, ``from_bytes``.
  - Add: APNG method ``append_file``, ``from_bytes``.
  - Add: module function ``parse_chunks``.
  - **Drop: module function `is_png` and `chunks`.**
  - **Change: `PNG.open` now only reads PNG images. To read non-PNG images, use `PNG.open_any`.**
  - **Change: `APNG.append` now only accepts `PNG` instance. To append PNG files, use `APNG.append_file`.**

- 0.2.1 (Apr 19, 2018)

  - Add: support num_plays. (`#4 <https://github.com/eight04/pyAPNG/issues/4>`_)

- 0.2.0 (Dec 8, 2017)

  - Add test.
  - Add documents.
  - Add: support path-like object.
  - Fix: some chunks must appear before IDAT. (`#1 <https://github.com/eight04/pyAPNG/issues/1>`_)
  - Fix: change chunks order in APNG. Some chunks are moved to the end of the file.
  - Fix: remove tRNS hack.
  - Fix: is_png shouldn't move file pointer. (`#2 <https://github.com/eight04/pyAPNG/pull/2>`_)

- 0.1.0 (May 30, 2016)

  - First release.
