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
mark_as_needing_update = __import__("mark-as-needing-update")

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
 ,mark_as_needing_update
 ]

for module in modules:
  print("Testing module: " + module.__name__)
  (failures,_) = doctest.testmod(module)
  if failures:
    sys.exit(failures)

print("Tests passed.")
