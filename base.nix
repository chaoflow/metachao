{ }:

with import <nixpkgs> {};

let
  base = {

  paths26 =
    [ python26
      python26Packages.coverage
      python26Packages.flake8
      python26Packages.ipdb
      python26Packages.ipdbplugin
      python26Packages.ipython
      python26Packages.nose
      python26Packages.pylint
      python26Packages.ordereddict
      python26Packages.recursivePthLoader
      python26Packages.sqlite3
      python26Packages.unittest2
      python26Packages.virtualenv
    ] ++ lib.attrValues python26.modules;

  paths27 =
    [ python27
      python27Packages.coverage
      python27Packages.flake8
      python27Packages.ipdb
      python27Packages.ipdbplugin
      python27Packages.ipython
      python27Packages.nose
      python27Packages.pylint
      python27Packages.recursivePthLoader
      python27Packages.sqlite3
      python27Packages.virtualenv
    ] ++ lib.attrValues python27.modules;

}; in base