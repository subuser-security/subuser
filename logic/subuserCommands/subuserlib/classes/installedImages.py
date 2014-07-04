#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import os,json,collections,sys
#internal imports
import subuserlib.classes.installedImage,subuserlib.classes.fileBackedObject, subuserlib.classes.userOwnedObject

class InstalledImages(list,subuserlib.classes.userOwnedObject.UserOwnedObject,subuserlib.classes.fileBackedObject.FileBackedObject):

  def reloadInstalledImagesRegistry(self):
    """ Reload the installed images list from disk, discarding the current in-memory version. """
    del self[:] # Clear the old list of InstalledImage objects.

    installedImagesPath = self.getUser().getConfig().getInstalledImagesDotJsonPath()
    if os.path.exists(installedImagesPath):
      with open(installedImagesPath, 'r') as file_f:
        try:
          installedImagesDict = json.load(file_f, object_pairs_hook=collections.OrderedDict)
        except ValueError:
          sys.exit("Error:  installed-images.json is not a valid JSON file. Perhaps it is corrupted.")
    else:
      installedImagesDict = {}
    # Create the InstalledImage objects.
    for imageID,imageAttributes in installedImagesDict.iteritems():
      image = subuserlib.classes.installedImage.InstalledImage(
        user=self.getUser(),
        imageID=imageID,
        lastUpdateTime=imageAttributes["last-update-time"],
        sourceName=imageAttributes["source-program"],
        sourceRepo=imageAttributes["source-repo"])
      self.append(image)
 
  def save(self):
    """ Save attributes of the installed images to disk. """
    # Build a dictionary of installed images.
    installedImagesDict = {}
    for installedImage in self:
      imageAttributes = {}
      imageAttributes["last-update-time"] = installedImage.getLastUpdateTime
      imageAttributes["source-repo"] = installedImage.getProgramSource().getRepository().getName()
      imageAttributes["source-program"] = installedImage.getProgramSource().getName()
      installedImagesDict[installedImage.getImageID] = imageAttributes

    # Write that dictionary to disk.
    installedImagesPath = self.getUser().config.getInstalledImagesDotJsonPath()
    with open(installedImagesPath, 'w') as file_f:
      json.dump(self.__installedImagesDict, file_f, indent=1, separators=(',', ': '))

  def __init__(self,user):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self.reloadInstalledImagesRegistry()

  def unregisterNonExistantImages(self):
    """
     Go through the installed images list and unregister any images that aren't actually installed.
    """
    filter(subuserlib.classes.installedImage.isDockerImageThere,self)
