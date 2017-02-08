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
  for _,subuser in user.registry.subusers.items():
    if subuser.imageId:
      try:
        installedImage = subuser.user.installedImages[subuser.imageId]
        for inUseInstalledImage in installedImage.getImageLineage():
          installedImagesThatAreInUse[inUseInstalledImage.imageId] = inUseInstalledImage
      except KeyError:
        user.registry.log("Warning: No image for %s installed."%subuser.name)
  return installedImagesThatAreInUse

def removeOldImages(user,dryrun=False,yes=False,sourceRepo=None,imageSourceName=None):
  installedImagesThatAreInUse = getInstalledImagesThatAreInUse(user)
  imagesToBeRemoved = []
  for installedImageId,installedImage in user.installedImages.items():
    if (   (not installedImageId in installedImagesThatAreInUse)
       and (not sourceRepo or installedImage.sourceRepoId == sourceRepo.id)
       and (not imageSourceName or installedImage.imageSourceName == imageSourceName)):
      imagesToBeRemoved.append(installedImage)
  if not imagesToBeRemoved:
    user.registry.log("There are no unused images to be removed.")
    return
  user.registry.log("The following images are uneeded and would be deleted.")
  user.registry.log("DOCKER-ID : SUBUSER-ID")
  # List images to be removed
  for installedImage in imagesToBeRemoved:
    user.registry.log("Removing unneeded image "+installedImage.imageId + " : " + installedImage.imageSource.getIdentifier())
  if dryrun:
    return
  # Ask user if we should continue?
  try:
    user.registry.log("Would you like to remove these images now? [Y/n]:",verbosityLevel=4)
    answer = input("Would you like to remove these images now? [Y/n]:")
    removeImages = not (answer == "n")
  except EOFError: # When not running interactively...
    user.registry.log("")
    removeImages = True
  if yes or removeImages:
    for installedImage in imagesToBeRemoved:
      installedImage.removeCachedRuntimes()
      installedImage.removeDockerImage()
    subuserlib.verify.verify(user)
    user.registry.commit()
