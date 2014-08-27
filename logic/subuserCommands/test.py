#!/usr/bin/python
import subuserlib.test

subuserlib.test.testing = True

import subuserlib.docker,subuserlib.basicPaths
if subuserlib.docker.getDockerExecutable():
  subuserlib.docker.runDockerAndExitIfItFails(["build","."],subuserlib.basicPaths.getSubuserDir())
  exit()

import doctest,sys,subprocess,os

subprocess.call(["/root/subuser/test/teardown"])
subprocess.call(["/root/subuser/test/setup"])

# classes
import subuserlib.classes.user,subuserlib.classes.subuser
# libs
import subuserlib.resolve
# commands
import list,describe
dry_run = __import__("dry-run")
mark_as_updated = __import__("mark-as-updated")
print_dependency_info = __import__("print-dependency-info")

modules = [
 # classes
 subuserlib.classes.user
 ,subuserlib.classes.subusers
 # subuserlib modules
 ,subuserlib.resolve
 # subuser commands
 ,dry_run
 ,list
 ,describe
 ,mark_as_updated
 ,print_dependency_info
 ]

for module in modules:
  print("Testing module: " + module.__name__)
  (failures,_) = doctest.testmod(module)
  if failures:
    sys.exit(failures)

print("Tests passed.")
