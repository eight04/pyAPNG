#! python3

import pathlib
from unittest import TestCase, main
from apng import is_png

class Main(TestCase):
	def test_is_png(self):
		file = pathlib.Path(__file__).joinpath("../test/test.png")
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

main()
