#!/usr/bin/python

import pathConfig
#external imports
import sys
import os
import io
#internal imports
import subuserlib.docker
import subuserlib.basicPaths

if "--help" in sys.argv:
  print("""Run the subuser test suit.  Please do this before sending pull requests.

Options include:

 - ``--travis`` - run the test suit in travis mode which does not run the tests in Docker.
 - ``--no-fail`` - do not stop the test suit from running after a test fails.

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

if subuserlib.docker.getDockerExecutable():
  from subuserlib.classes.docker.dockerDaemon import DockerDaemon
  import subuserlib.classes.docker.dockerDaemon
  from subuserlib.classes.fileStructure import BasicFileStructure
  dockerDaemon = DockerDaemon(MockUser())
  testDockerfileNames = [
   "Dockerfile-debian-python2",
   "Dockerfile-arch-python3",
  ]
  for testDockerfileName in testDockerfileNames:
    with io.open(os.path.join(subuserlib.basicPaths.getSubuserDir(),"test",testDockerfileName),encoding="utf-8",mode="r") as dockerfile:
      dockerfileContents = dockerfile.read()
    try:
      subuserDir = BasicFileStructure(subuserlib.basicPaths.getSubuserDir())
      dockerDaemon.build(repositoryFileStructure=subuserDir,relativeBuildContextPath="./",useCache=True,dockerfile=dockerfileContents)
    except subuserlib.classes.docker.dockerDaemon.ImageBuildException as e:
      print("Tests failed!")
      print(str(e))
      if not "--no-fail" in sys.argv:
        exit(1)
  exit()

import subuserlib.test

subuserlib.test.testing = True

import subuserlib.docker,sys,doctest,subprocess,os,subuserlib.paths

if not "--travis" in sys.argv:
  subuserDir = "/root/subuser"
else:
  subuserDir = subuserlib.paths.getSubuserDir()

subprocess.call([os.path.join(subuserDir,"test/teardown"),subuserDir])
subprocess.call([os.path.join(subuserDir,"test/setup"),subuserDir])

# classes
import subuserlib.classes.user
import subuserlib.classes.subuser
import subuserlib.classes.fileStructure
# libs
import subuserlib.resolve
import subuserlib.permissions
# commands
import list
import describe
import repository
import subuser
import update
dry_run = __import__("dry-run")
print_dependency_info = __import__("print-dependency-info")
remove_old_images = __import__("remove-old-images")

modules = [
  # classes
  subuserlib.classes.user
  ,subuserlib.classes.subusers
  ,subuserlib.classes.fileStructure
  # subuserlib modules
  ,subuserlib.permissions
  ,subuserlib.resolve
  # subuser commands
  ,dry_run
  ,list
  ,describe
  ,print_dependency_info
  ,remove_old_images
  ,repository
  ,subuser
  ,update
  ]

for module in modules:
  print("Testing module: " + module.__name__)
  (failures,_) = doctest.testmod(module)
  if failures:
    sys.exit(failures)

print("Tests passed.")
