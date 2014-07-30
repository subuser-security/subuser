#!/usr/bin/python
import subuserlib.test

subuserlib.test.testing = True

import subuserlib.docker,subuserlib.basicPaths
if subuserlib.docker.getDockerExecutable():
  subuserlib.docker.runDockerAndExitIfItFails(["build","."],subuserlib.basicPaths.getSubuserDir())
  exit()

import doctest,sys,subprocess,os

def setup():
  if not os.path.exists("/home"):
    subprocess.call("mkdir /home/",shell=True)
  subprocess.call("cp -r /root/subuser/test/home/ /home/test",shell=True)

def teardown(): # Normally teardown is not needed inside Docker, but sometimes I run these tests on a computer without Docker installed.
  if os.path.exists("/home/test"):
    subprocess.call("rm -r /home/test",shell=True)

teardown()
setup()

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
