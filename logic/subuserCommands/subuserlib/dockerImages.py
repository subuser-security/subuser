#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import subprocess
import availablePrograms
import utils
import json

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
 roughImagesList = subprocess.check_output(["docker","images"])
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

def inspectImage(imageTag):
 """ Returns a dictionary coresponding to the json outputed by docker inspect. """
 dockerInspectOutput = subprocess.check_output(["docker","inspect",imageTag])
 imageInfo = json.loads(dockerInspectOutput)
 return imageInfo[0]

def getImageID(imageTag):
 """ Returns the ID(as a string) of an image given that image's tag. """
 return inspectImage(imageTag)["id"]
