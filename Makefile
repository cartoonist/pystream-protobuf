PIP=pip
TEST=nosetests
TESTREPO=pypitest
MAINREPO=pypi

vpath %_pb2.py test/

# Specifying phony targets
.PHONY: init test dist-test dist

init:
	${PIP} install -r requirements.txt

vg_pb2.py:
	protoc -I=test/ --python_out=test/ test/vg.proto

test: vg_pb2.py
	${TEST}

README.rst: README.md
	pandoc -o $@ $<

VERSION:
	git describe --exact-match --tags $(git log -n1 --pretty=%h) > $@

dist-test: README.rst VERSION
	python setup.py register -r ${TESTREPO}
	python setup.py sdist upload -r ${TESTREPO}

dist: README.rst VERSION
	python setup.py register -r ${MAINREPO}
	python setup.py sdist upload -r ${MAINREPO}
