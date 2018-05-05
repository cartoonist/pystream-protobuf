PIP=pip
TESTREPO=pypitest
MAINREPO=pypi

vpath %_pb2.py test/

# Specifying phony targets
.PHONY: init test dist-test dist

init: vg_pb2.py
	${PIP} install -r requirements.txt

vg_pb2.py:
	protoc -I=test/ --python_out=test/ test/vg.proto

test: init
	python setup.py nosetests

dist-test:
	python setup.py register -r ${TESTREPO}
	python setup.py sdist upload -r ${TESTREPO}

dist:
	python setup.py register -r ${MAINREPO}
	python setup.py sdist upload -r ${MAINREPO}
