#!/usr/bin/python

import pathConfig
#external imports
import sys
import os
import io
import subprocess
#internal imports
import subuserlib.docker
import subuserlib.paths
import subuserlib.terminalColors
import subuserlib.paths

if "--help" in sys.argv:
  print("""Run the subuser test suit.  Please do this before sending pull requests.

Options include:

 - ``--travis`` - run the test suit in travis mode which does not run the tests in Docker.
 - ``--no-fail`` - do not stop the test suit from running after a test fails.
 - ``--x11-bridge`` - run x11 bridge test suit. To run the test suit, you must have a subuser named xterm which has the gui option enabled. You will be shown a series of xterms and two series of counters. You should close the xterms and see that the counters go up linearly.
 -- ``--skip-codetests`` - do not run doctests. Usefull for testing the X11 bridge exclusively.

""")
  sys.exit()

class MockRegistry():
  def __init__(self):
    pass
  def log(self,message):
    print(message)

class MockUser():
  def __init__(self):
    pass
  def getRegistry(self):
    return MockRegistry()

if subuserlib.docker.getExecutable():
  if not "--skip-codetests" in sys.argv:
    from subuserlib.classes.docker.dockerDaemon import DockerDaemon
    import subuserlib.classes.docker.dockerDaemon
    from subuserlib.classes.fileStructure import BasicFileStructure
    dockerDaemon = DockerDaemon(MockUser())
    testDockerfileNames = [
     "Dockerfile-arch-python3",
     "Dockerfile-debian-python2",
    ]
    for testDockerfileName in testDockerfileNames:
      with io.open(os.path.join(subuserlib.paths.getSubuserDir(),"test",testDockerfileName),encoding="utf-8",mode="r") as dockerfile:
        dockerfileContents = dockerfile.read()
      try:
        subuserDir = BasicFileStructure(subuserlib.paths.getSubuserDir())
        id = dockerDaemon.build(repositoryFileStructure=subuserDir,relativeBuildContextPath="./",useCache=True,dockerfile=dockerfileContents)
        if dockerDaemon.execute(["run","-it","--volume",subuserlib.paths.getSubuserDir()+":/root/subuser:ro",id,"/root/subuser/logic/subuser","test"]) != 0:
          raise Exception()
      except Exception as e:
        print(subuserlib.terminalColors.FAIL+"Tests failed!"+subuserlib.terminalColors.ENDC)
        print(str(e))
        if not "--no-fail" in sys.argv:
          exit(1)
  if "--x11-bridge" in sys.argv:
    pid = os.fork()
    if pid:
      counter = "a"
    else:
      counter = "b"
    for i in range(1,6):
      print(counter+" "+str(i))
      command = [os.path.join(subuserlib.paths.getSubuserDir(),"logic","subuser"),"run","xterm"]
      subprocess.call(command)
  exit()

import subuserlib.test

subuserlib.test.testing = True

import subuserlib.docker
import doctest

if not "--travis" in sys.argv:
  subuserDir = "/root/subuser"
else:
  subuserDir = subuserlib.paths.getSubuserDir()

subprocess.call([os.path.join(subuserDir,"test/setup"),subuserDir])

# classes
import subuserlib.classes.user
import subuserlib.classes.subuser
import subuserlib.classes.fileStructure
import subuserlib.classes.gitRepository
# libs
import subuserlib.resolve
import subuserlib.permissions
# commands
list = __import__("subuser-list")
version = __import__("subuser-version")
describe = __import__("subuser-describe")
repository = __import__("subuser-repository")
subuser = __import__("subuser-subuser")
update = __import__("subuser-update")
dry_run = __import__("subuser-dry-run")
print_dependency_info = __import__("subuser-print-dependency-info")
remove_old_images = __import__("subuser-remove-old-images")

modules = [
  # classes
  subuserlib.classes.user
  ,subuserlib.classes.subusers
  # subuserlib modules
  ,subuserlib.permissions
  ,subuserlib.resolve
  # subuser commands
  ,dry_run
  ,list
  ,version
  ,describe
  ,print_dependency_info
  ,remove_old_images
  ,repository
  ,subuser
  ,update
  ]

localOnlyModules = [ # These don't work with travis for some reason...
  subuserlib.classes.fileStructure
  ,subuserlib.classes.gitRepository]

if not "--travis" in sys.argv:
  modules.extend(localOnlyModules)

for module in modules:
  print(subuserlib.terminalColors.OKGREEN+"Testing module: " + module.__name__+subuserlib.terminalColors.ENDC)
  (failures,_) = doctest.testmod(module)
  if failures:
    sys.exit(failures)

print(subuserlib.terminalColors.OKGREEN+"Tests passed."+subuserlib.terminalColors.ENDC)
