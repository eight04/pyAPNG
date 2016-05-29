#! python3

import re

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

def read(file):
	with open(path.join(here, file), encoding='utf-8') as f:
		content = f.read()
	return content
	
def find_version(file):
	return re.search(r"__version__ = (\S*)", read(file)).group(1).strip("\"'")
	
setup(
	name = "apng",
	version = find_version("apng/__init__.py"),
	description = 'A python module to deal with APNG file.',
	long_description = read('README.rst'),
	url = 'https://github.com/eight04/pyAPNG',
	author = 'eight',
	author_email = 'eight04@gmail.com',
	license = 'MIT',
	# See https://pypi.python.org/pypi?%3Aaction=list_classifiers
	classifiers = [
		'Development Status :: 5 - Production/Stable',
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Natural Language :: Chinese (Traditional)",
		"Programming Language :: Python :: 3.5",
		"Topic :: Multimedia :: Graphics :: Graphics Conversion"
	],
	keywords = 'png apng image convert',
	packages = find_packages()
	# https://pythonhosted.org/setuptools/setuptools.html#declaring-dependencies
)
