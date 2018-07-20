#! python3
# coding=utf-8

import json
from apng import APNG

try:
	import pathlib2 as pathlib
except ImportError:
	import pathlib
	
try:
	import unittest2 as unittest
except ImportError:
	import unittest

try:
	import subprocess32 as subprocess
except ImportError:
	import subprocess
	
class MakeTextChunk(unittest.TestCase):
	def test_text(self):
		from apng import make_text_chunk, make_chunk
		chunk_type, data = make_text_chunk(value="some text")
		self.assertEqual(chunk_type, "tEXt")
		self.assertEqual(data, make_chunk("tEXt", b"Comment\0some text"))
		
	def test_ztxt(self):
		import zlib
		from apng import make_text_chunk, make_chunk
		chunk_type, data = make_text_chunk(type="zTXt", value="some text")
		self.assertEqual(chunk_type, "zTXt")
		self.assertEqual(data, make_chunk("zTXt", b"Comment\0\0" + zlib.compress(b"some text")))
		
	def test_itxt(self):
		from apng import make_text_chunk, make_chunk
		chunk_type, data = make_text_chunk(type="iTXt", value=u"ＳＯＭＥ　ＴＥＸＴ")
		self.assertEqual(chunk_type, "iTXt")
		self.assertEqual(data, make_chunk("iTXt", b"Comment\0\0\0\0\0" + u"ＳＯＭＥ　ＴＥＸＴ".encode("utf-8")))
		
	def test_itxt_compressed(self):
		import zlib
		from apng import make_text_chunk, make_chunk
		chunk_type, data = make_text_chunk(type="iTXt", value=u"ＳＯＭＥ　ＴＥＸＴ", compression_flag=1)
		self.assertEqual(chunk_type, "iTXt")
		self.assertEqual(
			data,
			make_chunk(
				"iTXt",
				b"Comment\0\1\0\0\0" +
					zlib.compress(u"ＳＯＭＥ　ＴＥＸＴ".encode("utf-8"))
			)
		)

class Functional(unittest.TestCase):
	def setUp(self):
		pathlib.Path("build").mkdir(parents=True, exist_ok=True)

	def test_assemble(self):
		def iter_frames(dir_):
			frames = {}
			for file in dir_.glob("frame-*"):
				if file.stem not in frames:
					frames[file.stem] = {"name": file.stem}
				frames[file.stem][file.suffix] = file
			for frame in sorted(frames.values(), key=lambda i: int(i["name"].partition("-")[-1])):
				if ".json" in frame:
					ctrl = json.loads(frame[".json"].read_text())
				else:
					ctrl = {}
				yield frame[".png"], ctrl
				
	
		for dir_ in pathlib.Path("test/fixtures").iterdir():
			with self.subTest("dir: {}".format(dir_.name)):
				try:
					options = json.loads(dir_.joinpath("property.json").read_text())
				except IOError:
					options = {}
				im = APNG(**options)
				for file, ctrl in iter_frames(dir_):
					im.append_file(file, **ctrl)
				filename = "{}-animated.png".format(dir_.stem)
				im.save(pathlib.Path("build").joinpath(filename))
				subprocess.run(
					"pngcheck {}".format(filename),
					cwd="build", shell=True, check=True
				)
				
	def test_disassemble(self):
		for dir_ in pathlib.Path("test/fixtures").iterdir():
			with self.subTest(dir_.stem):
				im = APNG.open(dir_.joinpath("animated.png"))
				options_file = dir_.joinpath("property.json")
				if options_file.exists():
					options = json.loads(options_file.read_text())
					for key, value in options.items():
						assert getattr(im, key) == value
				for i, (png, _ctrl) in enumerate(im.frames):
					filename = "{}-{}.png".format(dir_.stem, i + 1)
					png.save(pathlib.Path("build").joinpath(filename))
					subprocess.run(
						"pngcheck {}".format(filename),
						cwd="build", shell=True, check=True)

unittest.main()
