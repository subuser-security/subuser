#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
#import ...
#internal imports
import docker,dockerImages

def getRunningSubuserPrograms():
  """ Returns a list of the currently running subuser programs. """
  psOutput = docker.getDockerOutput(["ps","-q"])
  runningContainerIDs = filter(len,psOutput.split("\n")) #We filter out emty strings
  runningSubuserPrograms = set()
  for container in runningContainerIDs:
    containerImageTag = dockerImages.getContainerImageTag(container)
    subuserPrefix = "subuser-"
    if containerImageTag.startswith(subuserPrefix):
      runningSubuserPrograms.add(containerImageTag[len(subuserPrefix):])
  return list(runningSubuserPrograms)

def isProgramRunning(name):
  """ Returns True if the program is currently running. """
  return name in getRunningSubuserPrograms()

def areProgramsRunning(programs):
  """ Returns True if at least one of the listed programs is currently running. """
  return not (set(getRunningSubuserPrograms())&set(programs)) == set()