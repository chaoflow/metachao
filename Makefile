#
# The development checkouts will be installed as siblings to the
# current directory
#
REPOS_DIR=..

all: check

.nixenv: dev.nix
	nix-build --out-link nixenv -I ~/dev/nixos dev.nix
	touch .nixenv

bin/pip: .nixenv
	./nixenv/bin/virtualenv --distribute --clear .
	#rm ./bin/easy_install*
	#echo ../../../nixenv/lib/python2.7/site-packages > lib/python2.7/site-packages/nixenv.pth

.requirements: bin/pip requirements.txt setup.py
	./bin/pip install -r requirements.txt
	touch .requirements

print-syspath: .requirements
	./bin/python -c 'import sys,pprint;pprint.pprint(sys.path)'

check-imports: .requirements
	./bin/python -c 'import metachao'

nose: .requirements
	./bin/nosetests -w . --with-cov

nose2: .requirements
	./bin/nose2 --verbose --with-cov

check: check-imports nose

.PHONY: all print-syspath check check-imports nose2 nose
