#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import sys,os,stat
#internal imports
import permissions,paths,installTime,registry,dockerImages,docker,subprocessExtras

def installExecutable(programName):
  redirect="""#!/bin/bash\nsubuser run {0} $@\n""".format(programName)
  executablePath=paths.getExecutablePath(programName)
  with open(executablePath, 'w') as file_f:
    file_f.write(redirect)
    st = os.stat(executablePath)
    os.chmod(executablePath, stat.S_IMODE(st.st_mode) | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

def installFromBaseImage(programName,programSrcDir):
  buildImageScriptPath = paths.getBuildImageScriptPath(programSrcDir)
  #Report to user
  while True:
    sys.stdout.write("""\nATTENTION!!!

  You have asked to install the <{0}>. Doing so requires that the following shell script be run on your computer.
  SHELL SCRIPT PATH: <{1}>

  - Do quit [q] or press ENTER
  - Do you want to view the full contents of this shell script [v]?
  - Do you want to continue? (Type "run" to run the shell script)

  [v/run/q]: """.format(programName, buildImageScriptPath))
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
    with open(buildImageScriptPath, 'r') as file_f:
      print('\n===================== SCRIPT CODE =====================\n')
      print(file_f.read())
      print('\n===================== END SCRIPT CODE =====================\n')

    while True:
      sys.stdout.write("""SHELL SCRIPT PATH: <{0}>

    - Do quit [q] or press ENTER
    - Do you want to continue? (Type "run" to run the shell script)

    [run/q]: """.format(buildImageScriptPath))
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
    st = os.stat(buildImageScriptPath)
    os.chmod(buildImageScriptPath, stat.S_IMODE(st.st_mode) | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    subprocessExtras.subprocessCheckedCall([buildImageScriptPath])

def installFromDockerfile(programName, programSrcDir, useCache):
  if useCache:
    cacheArg = "--no-cache=false"
  else:
    cacheArg = "--no-cache=true"
  dockerImageDir = os.path.join(programSrcDir,"docker-image")
  docker.runDockerAndExitIfItFails(["build","--rm",cacheArg,"--tag=subuser-"+programName+"",dockerImageDir])


def installProgram(programName, useCache):
  """
  Build the docker image associated with a program and create a tiny executable to add that image to your path.
  """
  print("Installing {0} ...".format(programName))
  programSrcDir = paths.getProgramSrcDir(programName)
  _DockerfilePath = paths.getDockerfilePath(programSrcDir)
  # Check if we use a 'Dockerfile' or a 'BuildImage.sh'
  if os.path.isfile(paths.getBuildImageScriptPath(programSrcDir)):
    installFromBaseImage(programName,programSrcDir)
  elif os.path.isfile(_DockerfilePath):
    installFromDockerfile(programName,programSrcDir,useCache)
  else:
    sys.exit("No buildfile found: There needs to be a 'Dockerfile' or a 'BuildImage.sh' in the docker-image directory.")

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
  if dockerImages.isProgramsImageInstalled(programName):
    print("<{0}> is already installed.".format(programName))
  else:
    #get dependencytree and install bottom->up
    dependencyTree = reversed(registry.getDependencyTree(programName))
    programsToBeInstalled = []
    for dependency in dependencyTree:
      if not dockerImages.isProgramsImageInstalled(dependency):
        programsToBeInstalled.append(dependency)

    print("The following programs will be installed.")
    for program in programsToBeInstalled:
      print(program)

    for program in programsToBeInstalled:
      installProgram(program, useCache)
