LOCALISED_SCRIPTS = ipython ipdb flake8 pylint nose
PROJECT = $(shell basename $(shell pwd))

PYTHON_VERSION = 2.6
NIX_PROFILE = ./nixprofile${PYTHON_VERSION}
NIX_SITE = ${NIX_PROFILE}/lib/python${PYTHON_VERSION}/site-packages
VENV_CMD = ${NIX_PROFILE}/bin/virtualenv
VENV = .
VENV_SITE = ${VENV}/lib/python${PYTHON_VERSION}/site-packages
NOSETESTS = SLAPD=${SLAPD} ${VENV}/bin/nosetests


all: print-python-version test-import check

bootstrap:
	nix-env -p ${NIX_PROFILE} -i dev-env -f dev${PYTHON_VERSION}.nix
	${VENV_CMD} --distribute --clear .
	realpath --no-symlinks --relative-to ${VENV_SITE} ${NIX_SITE} > ${VENV_SITE}/nixprofile.pth
	${VENV}/bin/pip install -r requirements.txt --no-index -f ""
	for script in ${LOCALISED_SCRIPTS}; do ${VENV}/bin/easy_install -H "" $$script; done

print-syspath:
	${VENV}/bin/python -c 'import sys,pprint;pprint.pprint(sys.path)'

print-python-version:
	${VENV}/bin/python -c 'import sys; print sys.version'

test-import:
	${VENV}/bin/python -c "import ${PROJECT}; print ${PROJECT}"

var:
	test -L var -a ! -e var && rm var || true
	ln -s $(shell mktemp --tmpdir -d ${PROJECT}-var-XXXXXXXXXX) var

var-clean:
	rm -fR var/*

check: var var-clean
	${NOSETESTS} -v -w . --processes=4 ${ARGS}

check-debug: var var-clean
	DEBUG=1 ${NOSETESTS} -v -w . --ipdb --ipdb-failures ${ARGS}

coverage: var var-clean
	rm -f .coverage
	${NOSETESTS} -v -w . --with-cov --cover-branches --cover-package=${PROJECT} ${ARGS}


pyoc-clean:
	find . -name '*.py[oc]' -print0 |xargs -0 rm


.PHONY: all bootstrap check coverage print-syspath pyoc-clean test-nose var var-clean
