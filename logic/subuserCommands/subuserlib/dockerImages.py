#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import subprocess
import availablePrograms
import utils

def askToInstallProgram(programName):
 """ Asks the user if they want to install the given program.  If they say yes, install it, if they decline exit."""
 if not availablePrograms.available(programName):
  print(programName+" does not exist.")
  exit()
 if raw_input(programName+" is not installed. Do you want to install it now [y/n]?") == "y":
  utils.subprocessCheckedCall(["subuser","install",programName])
 else:
  exit()


def getImageTagOfInstalledProgram(programName):
 """ Return the tag of the docker image of an installed program. """
 roughImagesList = subprocess.check_output(["docker","images"])
 imagesListLines = roughImagesList.split("\n")
 imageTag = ""
 for line in imagesListLines:
  imageListingWords = line.split()
  if len(imageListingWords) > 1:
   if imageListingWords[0] == "subuser-"+programName:
    imageTag = "subuser-"+programName
 # The reason we do this complicated search mechanism is that it brings us closer to the goal of
 # tagging images with the userid as so: subuser-uid-programName.
 # Once we move to the new tagging system, it will be necessary to maintain compatibility with the old one for a time.
 # It may even be desired to allow images to be installed either globaly or "locally" aka userspecific.

 if imageTag == "":
  askToInstallProgram(programName)
  imageTag = "subuser-"+programName

 return imageTag
