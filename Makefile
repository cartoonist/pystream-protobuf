PIP=pip
TEST=nosetests
PKG_NAME=stream
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

dist-test: README.rst
	python setup.py register -r ${TESTREPO}
	python setup.py sdist upload -r ${TESTREPO}

dist: README.rst
	python setup.py register -r ${MAINREPO}
	python setup.py sdist upload -r ${MAINREPO}
