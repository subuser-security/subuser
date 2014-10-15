#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import subprocess,json,sys
#internal imports
import subprocessExtras,docker

def askToInstallImage(imageName):
  """ Asks the user if they want to install the given image.  If they say yes, install it, if they decline exit."""
  if not availableImages.available(imageName):
    sys.exit(imageName+" does not exist.")
  if raw_input(imageName+" is not installed. Do you want to install it now [y/n]?") == "y":
    subprocessExtras.subprocessCheckedCall(["subuser","install",imageName])
  else:
    sys.exit()

def getImageTagOfInstalledImage(image):
  """ Return a tag refering to the the docker image for an installed image.
If that image is not yet installed, install it.
  """
  if not isImagesImageInstalled(image):
    askToInstallImage(image)
  return "subuser-"+image

def isImagesImageInstalled(image):
  """ Return True if the images image tag is installed.  False otherwise. """
  return not (getImageID("subuser-"+image) == None)

def inspectImage(imageTagOrId):
  """ Returns a dictionary coresponding to the json outputed by docker inspect or None if the image does not exist. """
  try:
    dockerInspectOutput = docker.getDockerOutput(["inspect",imageTagOrId])
  except subprocess.CalledProcessError:
    return None
  imageInfo = json.loads(dockerInspectOutput)
  return imageInfo[0]

def getImageID(imageTag):
  """ Returns the ID(as a string) of an image given that image's lable. If no image has the given lable, return None."""
  imageInfo = inspectImage(imageTag)
  if imageInfo:
    return imageInfo["Id"] if "Id" in imageInfo else imageInfo["id"]
  else:
    return None

def getContainerInfo(containerID):
  inspectOutput = docker.getDockerOutput(["inspect",containerID])
  return json.loads(inspectOutput)

def getContainerImageTag(containerID):
  containerInfo = getContainerInfo(containerID)
  return containerInfo[0]["Config"]["Image"]

def getContainerImageID(containerID):
  containerInfo = getContainerInfo(containerID)
  return containerInfo[0]["Image"]

def removeImage(imageID):
  docker.runDocker(["rm",imageID])