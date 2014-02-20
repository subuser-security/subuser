#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import subprocess
import availablePrograms
import utils
import json
import docker

def askToInstallProgram(programName):
  """ Asks the user if they want to install the given program.  If they say yes, install it, if they decline exit."""
  if not availablePrograms.available(programName):
    print(programName+" does not exist.")
    exit()
  if raw_input(programName+" is not installed. Do you want to install it now [y/n]?") == "y":
    utils.subprocessCheckedCall(["subuser","install",programName])
  else:
    exit()

def getImageTagOfProgram(programName):
  """ Return the tag of a program or None, if there is no installed image for that program. """
  roughImagesList = docker.getDockerOutput(["images"])
  imagesListLines = roughImagesList.split("\n")
  imageTag = None
  for line in imagesListLines:
    imageListingWords = line.split()
    if len(imageListingWords) > 1:
      if imageListingWords[0] == "subuser-"+programName:
        imageTag = "subuser-"+programName
  # The reason we do this complicated search mechanism is that it brings us closer to the goal of
  # tagging images with the userid as so: subuser-uid-programName.
  # Once we move to the new tagging system, it will be necessary to maintain compatibility with the old one for a time.
  # It may even be desired to allow images to be installed either globaly or "locally" aka userspecific.
  return imageTag

def getImageTagOfInstalledProgram(programName):
  """ Return the tag of the docker image of an installed program.
If that program is not yet installed, install it.
  """
  imageTag = getImageTagOfProgram(programName)
  if imageTag == None:
    askToInstallProgram(programName)
    imageTag = "subuser-"+programName

  return imageTag

def isProgramsImageInstalled(programName):
  """ Return True if the programs image tag is installed.  False otherwise. """
  return not (getImageTagOfProgram(programName) == None)
  
def getParsedDockerImages(noTrunc=False):
  """ Parse `docker images` related output for easier access: return a dictionary of Columns Lists
  no-trunc: if False: truncate output 
  """
  dockerImageMatrix = {'REPOSITORY' : [], 'TAG' : [], 'ID' : [], 'CREATED' : [], 'SIZE' : []}
  if noTrunc:
    roughImagesList = docker.getDockerOutput(["images", "--no-trunc=true"])
  else:
    roughImagesList = docker.getDockerOutput(["images", "--no-trunc=false"])

  imagesLinesItemList = [line.split() for line in roughImagesList.split("\n") if line.split()]
  for itemList in imagesLinesItemList[1:]:
    dockerImageMatrix['REPOSITORY'].append(itemList[0])
    dockerImageMatrix['TAG'].append(itemList[1])
    dockerImageMatrix['ID'].append(itemList[2])
    dockerImageMatrix['CREATED'].append(' '.join([itemList[3], itemList[4], itemList[5]]))
    dockerImageMatrix['SIZE'].append(' '.join([itemList[6], itemList[7]]))
  return dockerImageMatrix

def inspectImage(imageTag):
  """ Returns a dictionary coresponding to the json outputed by docker inspect. """
  dockerInspectOutput = docker.getDockerOutput(["inspect",imageTag])
  imageInfo = json.loads(dockerInspectOutput)
  return imageInfo[0]

def getImageID(imageTag):
  """ Returns the ID(as a string) of an image given that image's tag. """
  return inspectImage(imageTag)["id"]

def getRunningProgramsWithNames(names):
  """ Returns a very crude listing from docker ps. Not a real list of the names of running programs or anything. """
  psOutput = docker.getDockerOutput(["ps"])
  psOutput = psOutput.split("\n")
  psOutput = psOutput[1:]
  def amongProgramsToBeWaitedOn(psOutputLine):
    tags = ["subuser-"+name for name in names]
    if psOutputLine == '': return False
    outputLineWords = psOutputLine.split()
    tagName = outputLineWords[1].split(':')[0]
    return tagName in tags
  return [psOutputLine for psOutputLine in psOutput if amongProgramsToBeWaitedOn(psOutputLine) ]

def isProgramRunning(name):
  """ Returns True if the program is currently running. """
  return len(getRunningProgramsWithNames([name])) > 0

def areProgramsRunning(programs):
  """ Returns True if at least one of the listed programs is currently running. """
  return len(getRunningProgramsWithNames(programs)) > 0
