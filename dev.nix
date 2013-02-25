# An environment to develop on dicttree.hydra
{ }:

with import <nixpkgs> {};

buildEnv {
  name = "dicttree-hydra-dev-env";
  paths = [
    python27
    #python27Packages.distribute
    python27Packages.ipdb
    python27Packages.ipython
    python27Packages.nose
    python27Packages.coverage
    #python27Packages.nose2
    #python27Packages.nose2Cov
    #python27Packages.pip
    python27Packages.recursivePthLoader
    python27Packages.sqlite3
    #python27Packages.unittest2
    python27Packages.virtualenv
    python27Packages.zope_interface
    #pythonLinkmeWrapper
  ] ++ lib.attrValues python27.modules;
}