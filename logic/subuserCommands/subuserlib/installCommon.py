#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import sys
import os
import stat
import utils
import permissions
import paths
import installTime
import registry
import dockerImages
import docker

def installExecutable(programName):
  redirect="""#!/bin/bash\nsubuser run {0} $@\n""".format(programName)
  executablePath=paths.getExecutablePath(programName)
  with open(executablePath, 'w') as file_f:
    file_f.write(redirect)
    st = os.stat(executablePath)
    os.chmod(executablePath, stat.S_IMODE(st.st_mode) | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

def installFromBaseImage(programName):
  makeBaseImageScriptPath = paths.getMakeBaseImageScriptPath(programName)
  #Report to user
  while True:
    sys.stdout.write("""\nATTENTION!!!

  You have asked to install the <{0}>. Doing so requires that the following shell script be run on your computer.
  SHELL SCRIPT PATH: <{1}>

  - Do quit [q] or press ENTER
  - Do you want to view the full contents of this shell script [v]?
  - Do you want to continue? (Type "run" to run the shell script)

  [v/run/q]: """.format(programName, paths.getMakeBaseImageScriptPath(programName)))
    sys.stdout.flush()
    try:
      userInput = sys.stdin.readline().strip()
      if not userInput:
        sys.exit("\nOperation aborted.  Exiting.")
      else:
        break
    except KeyboardInterrupt:
      sys.exit("\nOperation aborted.  Exiting.")

  if userInput == "v":
    with open(makeBaseImageScriptPath, 'r') as file_f:
      print('\n===================== SCRIPT CODE =====================\n')
      print(file_f.read())
      print('\n===================== END SCRIPT CODE =====================\n')

    while True:
      sys.stdout.write("""SHELL SCRIPT PATH: <{0}>

    - Do quit [q] or press ENTER
    - Do you want to continue? (Type "run" to run the shell script)

    [run/q]: """.format(makeBaseImageScriptPath))
      sys.stdout.flush()
      try:
        userInput = sys.stdin.readline().strip()
        if userInput != "run":
          sys.exit("\nOperation aborted.  Exiting.")
        else:
          break
      except KeyboardInterrupt:
        sys.exit("\nOperation aborted.  Exiting.")

  if userInput == "run":
    #Do the installation via SHELL SCRIPT
    st = os.stat(makeBaseImageScriptPath)
    os.chmod(makeBaseImageScriptPath, stat.S_IMODE(st.st_mode) | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    utils.subprocessCheckedCall([makeBaseImageScriptPath])


def installProgram(programName, useCache):
  """
  Build the docker image associated with a program and create a tiny executable to add that image to your path.
  """
  print("Installing {0} ...".format(programName))

  dockerImageDir = os.path.join(paths.getProgramSrcDir(programName), "docker-image")
  _DockerfilePath = os.path.join(dockerImageDir, 'Dockerfile')
  # Check if we use a 'Dockerfile' or a 'MakeBaseImage.sh'
  if os.path.isfile(paths.getMakeBaseImageScriptPath(programName)):
    installFromBaseImage(programName, cacheArg)
  elif os.path.isfile(_DockerfilePath):
    if useCache:
      cacheArg = "--no-cache=false"
    else:
      cacheArg = "--no-cache=true"
    docker.runDockerAndExitIfItFails(["build","-rm",cacheArg,"--tag=subuser-"+programName+"",dockerImageDir])
  else:
    sys.exit("No buildfile found: need one of: 'Dockerfile' or 'MakeBaseImage.sh'. PATH: {0}".format(dockerImageDir))

  _permissions = permissions.getPermissions(programName)

  # Create a small executable that just calls the real executable in the docker image.
  if 'executable' in _permissions:
    installExecutable(programName)

  try:
    lastUpdateTime = _permissions["last-update-time"]
  except KeyError:
    lastUpdateTime = installTime.currentTimeString()

  imageID = dockerImages.getImageID("subuser-{0}".format(programName))
  registry.registerProgram(programName, lastUpdateTime, imageID)

def installProgramAndDependencies(programName, useCache):
  """
  Build the dependencytree and install bottom->up
  """
  if registry.isProgramInstalled(programName):
    print("<{0}> is already installed.".format(programName))
  else:
    #get dependencytree and install bottom->up
    dependencyTree = reversed(registry.getDependencyTree(programName))
    programsToBeInstalled = []
    for dependency in dependencyTree:
      if not registry.isProgramInstalled(dependency):
        programsToBeInstalled.append(dependency)

    print("The following programs will be installed.")
    for program in programsToBeInstalled:
      print(program)

    for program in programsToBeInstalled:
      installProgram(program, useCache)
