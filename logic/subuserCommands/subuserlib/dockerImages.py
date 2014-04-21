#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import subprocess,json,sys
#internal imports
import subprocessExtras,availablePrograms,docker

def askToInstallProgram(programName):
  """ Asks the user if they want to install the given program.  If they say yes, install it, if they decline exit."""
  if not availablePrograms.available(programName):
    sys.exit(programName+" does not exist.")
  if raw_input(programName+" is not installed. Do you want to install it now [y/n]?") == "y":
    subprocessExtras.subprocessCheckedCall(["subuser","install",programName])
  else:
    sys.exit()

def getImageTagOfInstalledProgram(program):
  """ Return a tag refering to the the docker image for an installed program.
If that program is not yet installed, install it.
  """
  if not isProgramsImageInstalled(program):
    askToInstallProgram(program)
  return "subuser-"+program

def isProgramsImageInstalled(program):
  """ Return True if the programs image tag is installed.  False otherwise. """
  return not (getImageID("subuser-"+program) == None)

def inspectImage(imageTag):
  """ Returns a dictionary coresponding to the json outputed by docker inspect. """
  try:
    dockerInspectOutput = docker.getDockerOutput(["inspect",imageTag])
  except subprocess.CalledProcessError:
    return None
  imageInfo = json.loads(dockerInspectOutput)
  return imageInfo[0]

def getImageID(imageTag):
  """ Returns the ID(as a string) of an image given that image's lable. If no image has the given lable, return None."""
  imageInfo = inspectImage(imageTag)
  if imageInfo:
    return imageInfo["id"]
  else:
    return None

def getContainerImageTag(containerID):
  inspectOutput = docker.getDockerOutput(["inspect",containerID])
  containerInfo = json.loads(inspectOutput)
  return containerInfo[0]["Config"]["Image"]