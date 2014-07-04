#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
#import ...
#internal imports
import docker,dockerImages

def getRunningContainerIds():
  psOutput = docker.getDockerOutput(["ps","-q"])
  runningContainerIDs = filter(len,psOutput.split("\n")) #We filter out emty strings
  return runningContainerIDs

def getRunningImages():
  """ Returns a list of IDs of images with currently running containers. """
  runningContainerIDs = getRunningContainerIDs()
  runningImages = set()
  for container in runningContainerIDs:
    containerImageID = dockerImages.getContainerImageID(container)
    runningImages.add(containerImageID)
  return list(runningImages)

def isImageRunning(imageID):
  """ Returns True if the image currently has a running container based on it. """
  return name in getRunningImages()

def areImagesRunning(imageIDs):
  """ Returns True if at least one of the listed images currently has a running container based on it. """
  return not (set(getRunningImages())&set(programs)) == set()