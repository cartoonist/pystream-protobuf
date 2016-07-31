PIP=pip
TEST=nosetests
TESTREPO=pypitest
MAINREPO=pypi

# Specifying phony targets
.PHONY: init test dist-test dist

init:
	${PIP} install -r requirements.txt

test:
	${TEST}

dist-test:
	pandoc -o README.rst README.md
	python setup.py register -r ${TESTREPO}
	python setup.py sdist upload -r ${TESTREPO}

dist:
	pandoc -o README.rst README.md
	python setup.py register -r ${MAINREPO}
	python setup.py sdist upload -r ${MAINREPO}
