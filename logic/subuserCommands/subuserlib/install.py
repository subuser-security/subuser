#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import sys,os,stat
#internal imports
import permissions,paths,installTime,registry,dockerImages,docker,subprocessExtras

def installExecutable(programName):
  """
Install a trivial executable script into the PATH which launches the subser program.
  """
  redirect="""#!/bin/bash
subuser run """+programName+""" $@
"""
  executablePath=paths.getExecutablePath(programName)
  with open(executablePath, 'w') as file_f:
    file_f.write(redirect)
    st = os.stat(executablePath)
    os.chmod(executablePath, stat.S_IMODE(st.st_mode) | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

def installFromBaseImage(programName,programSrcDir):
  """
Build a docker base image using a script and then install that base image.
  """
  buildImageScriptPath = paths.getBuildImageScriptPath(programSrcDir)
  print("""\nATTENTION!

  Installing <"""+programName+"""> requires that the following shell script be run on your computer: <"""+buildImageScriptPath+"""> If you do not trust this shell script do not run it as it may be faulty or malicious!

  - Do you want to view the full contents of this shell script [v]?
  - Do you want to continue? (Type "run" to run the shell script)
  - To quit, press [q].

  [v/run/Q]: """)
  try:
    userInput = sys.stdin.readline().strip()
  except KeyboardInterrupt:
    sys.exit("\nOperation aborted.  Exiting.")

  if userInput == "v":
    print('\n===================== SCRIPT CODE =====================\n')
    with open(buildImageScriptPath, 'r') as file_f:
      print(file_f.read())
    print('\n===================== END SCRIPT CODE =====================\n')
    return installFromBaseImage(programName,programSrcDir)
  
  if userInput == "run":
    #Do the installation via SCRIPT
    st = os.stat(buildImageScriptPath)
    os.chmod(buildImageScriptPath, stat.S_IMODE(st.st_mode) | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    subprocessExtras.subprocessCheckedCall([buildImageScriptPath])
    return

  sys.exit("Will not run install script.  Nothing to do.  Exiting.")

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
  print("Installing "+programName+" ...")
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

  imageID = dockerImages.getImageID("subuser-"+programName)
  registry.registerProgram(programName, lastUpdateTime, imageID)

def getUniqueNameForProgram(sourceRepo,sourceName):
  """ It is possible that a programs name is not unique.  That is, another program in another repo may exist with the same name. Generate a unique name for each program, either by asking the user to enter a new name for the program or(in the case of libraries) by concatinating the program name with the name of the repo in which it resides.

  At the same time, ensure that the program will not unexpectedly interfere with any programs already in the PATH, by prompting the user if they want to rename the program in the case that the program has the same name as a program already in the PATH.

  """
  

def installProgramAndDependencies(programName, useCache):
  """
  Build the dependencytree and install bottom->up
  """
  if dockerImages.isProgramsImageInstalled(programName):
    print(programName+" is already installed.")
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
