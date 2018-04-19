#! python3

import io
import json
import pathlib
import subprocess
import tempfile
from unittest import TestCase, main
from apng import is_png, APNG

class Main(TestCase):
	def test_is_png(self):
		file = pathlib.Path("test/ball/animated.png")
		with self.subTest("file name"):
			assert is_png(str(file))
			
		with self.subTest("file-like"):
			with file.open("rb") as f:
				assert is_png(f)
				
		with self.subTest("shouldn't touch file pointer"):
			with file.open("rb") as f:
				is_png(f)
				assert f.tell() == 0
				
		with self.subTest("bytes"):
			assert is_png(file.read_bytes())
			
		with self.subTest("path-like"):
			assert is_png(file)

class Functional(TestCase):
	def test_assemble(self):
		def iter_frames(dir):
			frames = {}
			for file in dir.glob("frame-*"):
				if file.stem not in frames:
					frames[file.stem] = {"name": file.stem}
				frames[file.stem][file.suffix] = file
			for frame in sorted(frames.values(), key=lambda i: int(i["name"].partition("-")[-1])):
				if ".json" in frame:
					ctrl = json.loads(frame[".json"].read_text())
				else:
					ctrl = {}
				yield frame[".png"], ctrl
				
	
		for dir in pathlib.Path("test").iterdir():
			with self.subTest("dir: {}".format(dir.name)):
				try:
					property = json.loads(dir.joinpath("property.json").read_text())
				except OSError:
					property = {}
				im = APNG(**property)
				for png, ctrl in iter_frames(dir):
					im.append(png, **ctrl)
				filename = "{}-animated.png".format(dir.stem)
				im.save(pathlib.Path("build").joinpath(filename))
				subprocess.run(
					["pngcheck", filename],
					cwd="build", shell=True, check=True
				)
				
	def test_disassemble(self):
		for dir in pathlib.Path("test").iterdir():
			with self.subTest(dir.stem):
				im = APNG.open(dir.joinpath("animated.png"))
				property = dir.joinpath("property.json")
				if property.exists():
					property = json.loads(property.read_text())
					for key, value in property.items():
						assert getattr(im, key) == value
				for i, (png, ctrl) in enumerate(im.frames):
					filename = "{}-{}.png".format(dir.stem, i + 1)
					png.save(pathlib.Path("build").joinpath(filename))
					subprocess.run(
						["pngcheck", filename],
						cwd="build", shell=True, check=True)

main()
