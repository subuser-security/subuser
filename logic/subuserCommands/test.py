#!/usr/bin/python
import subuserlib.test

subuserlib.test.testing = True

import subuserlib.docker,subuserlib.basicPaths,subuserlib.subprocessExtras
if subuserlib.docker.getDockerExecutable():
  subuserlib.docker.runDockerAndExitIfItFails(["build","."],subuserlib.basicPaths.getSubuserDir())
  exit()

import doctest,sys,subprocess,os

def setup():
  if not os.path.exists("/home"):
    subprocess.call("mkdir /home/",shell=True)
  subprocess.call("cp -r /root/subuser/test/home/ /home/test",shell=True)
  subuserlib.subprocessExtras.subprocessCheckedCall(["git","init"],cwd="/root/subuser/test/remote-test-repo/")
  subuserlib.subprocessExtras.subprocessCheckedCall(["git","add","bar/permissions.json","bar/docker-image/Dockerfile"],cwd="/root/subuser/test/remote-test-repo/")
  subuserlib.subprocessExtras.subprocessCheckedCall(["git","commit","-m","'test'"],cwd="/root/subuser/test/remote-test-repo/")

def teardown(): # Normally teardown is not needed inside Docker, but sometimes I run these tests on a computer without Docker installed.
  if os.path.exists("/home/test"):
    subprocess.call("rm -r /root/subuser/test/remote-test-repo/.git",shell=True)
  subprocess.call("rm -r /home/test",shell=True)

teardown()
setup()

# classes
import subuserlib.classes.user,subuserlib.classes.subuser
# libs
import subuserlib.resolve
# commands
import list
dry_run = __import__("dry-run")

modules = [
 # classes
 subuserlib.classes.user
 ,subuserlib.classes.subusers
 # subuserlib modules
 ,subuserlib.resolve
 # subuser commands
 ,dry_run
 ,list
 ]

for module in modules:
  print("Testing module: " + module.__name__)
  (failures,_) = doctest.testmod(module)
  if failures:
    sys.exit(failures)

print("Tests passed.")
