#!/usr/bin/python
import pathConfig,subuserlib.docker,os,subuserlib.basicPaths,sys,io

if "--help" in sys.argv:
  print("Run the subuser test suit.  Please do this before sending pull requests.")
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
  import subuserlib.classes.dockerDaemon
  dockerDaemon = subuserlib.classes.dockerDaemon.DockerDaemon(MockUser())
  testDockerfileNames = ["Dockerfile-debian-python2",
                        "Dockerfile-arch-python3"]
  for testDockerfileName in testDockerfileNames:
    with io.open(os.path.join(subuserlib.basicPaths.getSubuserDir(),"test",testDockerfileName),encoding="utf-8",mode="r") as dockerfile:
      dockerfileContents = dockerfile.read()
    try:
      dockerDaemon.build(directoryWithDockerfile=subuserlib.basicPaths.getSubuserDir(),useCache=True,dockerfile=dockerfileContents)
    except subuserlib.classes.dockerDaemon.ImageBuildException as e:
      print("Tests failed!")
      print(str(e))
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
import subuserlib.classes.user,subuserlib.classes.subuser
# libs
import subuserlib.resolve
# commands
import list,describe,repository,subuser,update
dry_run = __import__("dry-run")
print_dependency_info = __import__("print-dependency-info")
remove_old_images = __import__("remove-old-images")

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
