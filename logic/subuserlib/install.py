#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
Implements functions involved in building/installing/updating subuser images.
"""

#external imports
import sys
#internal imports
import subuserlib.classes.installedImage
import subuserlib.installedImages
import subuserlib.verify

def cleanUpAndExitOnError(user,error):
  user.getRegistry().log(str(error))
  user.getRegistry().log("Cleaning up.")
  sys.exit(1)

def installImage(imageSource,parent=None):
  """
  Install a image by building the given ImageSource.
  Register the newly installed image in the user's InstalledImages list.
  Return the Id of the newly installedImage.
  """
  imageSource.getUser().getRegistry().logChange("Installing "+imageSource.getName()+" ...")
  imageId = imageSource.build(parent)
  imageSource.getUser().getInstalledImages()[imageId] = subuserlib.classes.installedImage.InstalledImage(imageSource.getUser(),imageId,imageSource.getName(),imageSource.getRepository().getName(),imageSource.getHash())
  imageSource.getUser().getInstalledImages().save()
  return imageId

def getImageSourceLineage(imageSource):
  """
  Return the lineage of the ProgrmSource, going from its base dependency up to itself.
  """
  sourceLineage = []
  while imageSource:
    sourceLineage.append(imageSource)
    try:
      imageSource = imageSource.getDependency()
    except SyntaxError as syntaxError:
      cleanUpAndExitOnError(imageSource.getUser(),"Error while building image: "+ str(syntaxError))
  return reversed(sourceLineage)

def doImagesMatch(installedImage,imageSource):
  return installedImage.getImageSourceName() == imageSource.getName() and installedImage.getSourceRepoId() == imageSource.getRepository().getName()

def doImageSourceHashesMatch(installedImage,imageSource):
  return installedImage.getImageSourceHash() == imageSource.getHash()

def compareSourceLineageAndInstalledImageLineage(user,sourceLineage,installedImageLineage):
  if not len(list(sourceLineage)) == len(installedImageLineage):
    user.getRegistry().log("Number of dependencies changed from "+str(len(installedImageLineage))+" to "+str(len(sourceLineage)))
    print("Image sources:")
    for imageSource in sourceLineage:
      print(imageSource.getName())
    print("Installed images:")
    for installedImage in installedImageLineage:
      print(installedImage.getImageSourceName())
    return False
  lineage = zip(sourceLineage,installedImageLineage)
  for imageSource,installedImage in lineage:
    imagesMatch =  doImagesMatch(installedImage,imageSource)
    imageSourceHashesMatch = doImageSourceHashesMatch(installedImage,imageSource)
    if not (imagesMatch and imageSourceHashesMatch):
      if not imagesMatch:
        user.getRegistry().log("Dependency changed for image from "+installedImage.getImageSourceName()+"@"+installedImage.getSourceRepoId()+" to "+imageSource.getName()+"@"+imageSource.getRepository().getName())
      elif not imageSourceHashesMatch:
        user.getRegistry().log("Installed image "+installedImage.getImageSourceName()+"@"+installedImage.getSourceRepoId()+" is out of date.\nCurrently installed from image source:\n "+installedImage.getImageSourceHash()+"\nCurrent version:\n "+str(imageSource.getPermissions()["last-update-time"])+"\n")
      return False
  return True

def isInstalledImageUpToDate(installedImage,checkForUpdatesExternally=False):
  """
  Returns True if the installed image(including all of its dependencies, is up to date.  False otherwise.
  """
  try:
    topImageSource = installedImage.getUser().getRegistry().getRepositories()[installedImage.getSourceRepoId()][installedImage.getImageSourceName()]
  except KeyError: # Image source not found, therefore updating would be pointless.
    return True
  # Check for updates to image sources
  sourceLineage = getImageSourceLineage(topImageSource)
  installedImageLineage = subuserlib.installedImages.getImageLineage(installedImage.getUser(),installedImage.getImageId())
  if not compareSourceLineageAndInstalledImageLineage(installedImage.getUser(),sourceLineage,installedImageLineage):
    return False
  # Check for updates externally using the images' built in check-for-updates script.
  if checkForUpdatesExternally:
    if installedImage.checkForUpdates():
      return False
  return True

def ensureSubuserImageIsInstalledAndUpToDate(subuser, checkForUpdatesExternally=False):
  """
  Ensure that the Docker image associated with the subuser is installed and up to date.
  If the image is already installed, but is out of date, or it's dependencies are out of date, build it again.
  Otherwise, do nothing.
  """
  subuser.getUser().getRegistry().log("Checking if subuser "+subuser.getName()+" is up to date.")
  # get dependency list as a list of ImageSources
  sourceLineage = getImageSourceLineage(subuser.getImageSource())
  # We go through the sourceLineage as if it where a todo list of dependencies to fulfill
  aDependencyChangedReinstallEverythingFromNowOn = False
  previousImageId = None
  for imageSource in sourceLineage:
    latestInstalledImage = imageSource.getLatestInstalledImage()
    if not aDependencyChangedReinstallEverythingFromNowOn:
      if latestInstalledImage and isInstalledImageUpToDate(latestInstalledImage,checkForUpdatesExternally=checkForUpdatesExternally):
        previousImageId = latestInstalledImage.getImageId()
        continue
      else:
        aDependencyChangedReinstallEverythingFromNowOn = True
    assert aDependencyChangedReinstallEverythingFromNowOn
    previousImageId = installImage(imageSource,parent=previousImageId)
  if not subuser.getImageId() == previousImageId:
    subuser.setImageId(previousImageId)
    subuser.getUser().getRegistry().logChange("Installed new image <"+subuser.getImageId()+"> for subuser "+subuser.getName())
