# https://github.com/PyCQA/pylint/issues/1368
# pylint: disable=bad-whitespace
import sys
from xcute import cute, Skip, LiveReload

cute(
	pkg_name = "apng",
	lint = Skip("pylint cute.py test apng", sys.version_info < (3, )),
	test = [
		"lint",
		"pytest -x test",
		"readme_build"
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
	install = 'python -m pip install -e .',
	readme_build = [
		'python setup.py --long-description | x-pipe build/readme/index.rst',
		'rst2html5.py --no-raw --exit-status=1 --verbose '
			'build/readme/index.rst build/readme/index.html'
	],
	readme_pre = "readme_build",
	readme = LiveReload("README.rst", "readme_build", "build/readme"),
	doc_build = "sphinx-build docs build/docs",
	doc_pre = "doc_build",
	doc = LiveReload(["{pkg_name}", "docs"], "doc_build", "build/docs")
)
