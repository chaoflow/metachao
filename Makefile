all: check

bootstrap: dev.nix requirements.txt setup.py
	nix-build --out-link nixenv dev.nix
	./nixenv/bin/virtualenv --distribute --clear .
	echo ../../../nixenv/lib/python2.7/site-packages > lib/python2.7/site-packages/nixenv.pth
	./bin/pip install -r requirements.txt --no-index -f ""
	./bin/easy_install -H "" metachao[test]

bin/nosetests:
	./bin/easy_install -H "" nose

print-syspath:
	./bin/python -c 'import sys,pprint;pprint.pprint(sys.path)'

test-nose: bin/nosetests
	rm -f .coverage
	./bin/nosetests -w . --with-cov --cover-branches --cover-package=metachao

check: test-nose

.PHONY: all bootstrap print-syspath check test-nose
