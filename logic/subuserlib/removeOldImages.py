# -*- coding: utf-8 -*-

#external imports
#import
#internal imports
import subuserlib.verify
import subuserlib.print

def getInstalledImagesThatAreInUse(user):
  """
  Returns a dictionary of currently installed images that are currently used by a subsuser directly, or indirectly (as a dependency of another image).

  Returns {imageId(string) : InstalledImage}
  """
  installedImagesThatAreInUse = {} # {imageId : installedImage}
  for _,subuser in user.getRegistry().getSubusers().items():
    if subuser.getImageId():
      try:
        installedImage = subuser.getUser().getInstalledImages()[subuser.getImageId()]
        for inUseInstalledImage in installedImage.getImageLineage():
          installedImagesThatAreInUse[inUseInstalledImage.getImageId()] = inUseInstalledImage
      except KeyError:
        user.getRegistry().log("Warning: No image for %s installed."%subuser.getName())
  return installedImagesThatAreInUse

def removeOldImages(user,dryrun=False,yes=False,sourceRepo=None,imageSourceName=None):
  installedImagesThatAreInUse = getInstalledImagesThatAreInUse(user)
  imagesToBeRemoved = []
  for installedImageId,installedImage in user.getInstalledImages().items():
    if (   (not installedImageId in installedImagesThatAreInUse)
       and (not sourceRepo or installedImage.getSourceRepoId() == sourceRepo.getId())
       and (not imageSourceName or installedImage.getImageSourceName() == imageSourceName)):
      imagesToBeRemoved.append(installedImage)
  if not imagesToBeRemoved:
    user.getRegistry().log("There are no unused images to be removed.")
    return
  user.getRegistry().log("The following images are uneeded and would be deleted.")
  user.getRegistry().log("DOCKER-ID : SUBUSER-ID")
  # List images to be removed
  for installedImage in imagesToBeRemoved:
    user.getRegistry().log("Removing unneeded image "+installedImage.getImageId() + " : " + installedImage.getImageSource().getIdentifier())
  if dryrun:
    return
  # Ask user if we should continue?
  try:
    user.getRegistry().log("Would you like to remove these images now? [Y/n]:",verbosityLevel=4)
    answer = input("Would you like to remove these images now? [Y/n]:")
    removeImages = not (answer == "n")
  except EOFError: # When not running interactively...
    user.getRegistry().log("")
    removeImages = True
  if yes or removeImages:
    for installedImage in imagesToBeRemoved:
      installedImage.removeCachedRuntimes()
      installedImage.removeDockerImage()
    subuserlib.verify.verify(user)
    user.getRegistry().commit()
