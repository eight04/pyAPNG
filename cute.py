#! python3

from xcute import cute, conf, exc

cute(
	pkg_name = "apng",
	test = ['python test.py', 'readme_build'],
	bump_pre = 'test',
	bump_post = ['dist', 'release', 'publish', 'install'],
	dist = 'rm -r build dist & python setup.py sdist bdist_wheel',
	release = [
		'git add .',
		'git commit -m "Release v{version}"',
		'git tag -a v{version} -m "Release v{version}"'
	],
	publish = [
		'twine upload dist/*{version}[.-]*',
		'git push --follow-tags'
	],
	publish_err = 'start https://pypi.python.org/pypi/{pkg_name}/',
	install = 'pip install -e .',
	install_err = 'elevate -c -w pip install -e .',
	readme_build = [
		'python setup.py --long-description | x-pipe build/ld.rst',
		'rst2html --no-raw --exit-status=1 --verbose '
			'build/ld.rst build/ld.html'
	],
	readme_build_err = ['readme_show', exc],
	readme_show = 'start build/ld.html',
	readme = 'readme_build',
	readme_post = 'readme_show'
)
