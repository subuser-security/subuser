#!/usr/bin/python
import subuserlib.test
subuserlib.test.testing = True

import doctest,sys

import subuserlib.classes.user,subuserlib.classes.subuser, list
dry_run = __import__("dry-run")

modules = [
 subuserlib.classes.user
 ,subuserlib.classes.subusers
 ,dry_run
 ,list]

for module in modules:
  print("Testing module: " + module.__name__)
  (failures,_) = doctest.testmod(module)
  if failures:
    sys.exit(failures)

print("Tests passed.")
