#! python3

import sys
from xcute import cute, Skip

def readme():
	"""Live reload readme"""
	from livereload import Server
	server = Server()
	server.watch("README.rst", "py cute.py readme_build")
	server.serve(open_url_delay=1, root="build/readme")
	
IS_LATEST = sys.version_info[:2] == (3, 6)
	
cute(
	pkg_name = "apng",
	lint = "pylint cute.py test.py apng",
	test = [
		"lint",
		'{py:2} test.py',
		'{py:3} test.py',
		'readme_build'
	],
	bump_pre = 'test',
	bump_post = ['dist', 'release', 'publish', 'install'],
	clean = "x-clean build dist",
	dist = [
		"clean",
		"python setup.py sdist bdist_wheel"
	],
	release = [
		'git add .',
		'git commit -m "Release v{version}"',
		'git tag -a v{version} -m "Release v{version}"'
	],
	publish = [
		'twine upload dist/*',
		'git push --follow-tags'
	],
	install = 'pip install -e .',
	readme_build = [
		'python setup.py --long-description | x-pipe build/readme/index.rst',
		'rst2html5.py --no-raw --exit-status=1 --verbose '
			'build/readme/index.rst build/readme/index.html'
	],
	readme_pre = "readme_build",
	readme = readme,
	doc = 'sphinx-autobuild -B -z {pkg_name} docs docs/build',
	travis = [Skip("lint", not IS_LATEST), "python test.py", "readme_build"]
)
