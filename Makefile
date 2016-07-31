PIP=pip
TEST=nosetests

# Specifying phony targets
.PHONY: init test

init:
	${PIP} install -r requirements.txt

test:
	${TEST}
