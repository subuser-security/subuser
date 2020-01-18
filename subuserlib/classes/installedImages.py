# -*- coding: utf-8 -*-

"""
This is the set of installed images that bellongs to a given user.
"""

#external imports
import os
import json
from collections import OrderedDict
import sys
#internal imports
from subuserlib.classes.installedImage import InstalledImage
from subuserlib.classes.fileBackedObject import FileBackedObject
from subuserlib.classes.userOwnedObject import UserOwnedObject

class InstalledImages(OrderedDict,UserOwnedObject,FileBackedObject):
  def __init__(self,user):
    UserOwnedObject.__init__(self,user)
    super().__init__()
    self.reloadInstalledImagesList()

  def reloadInstalledImagesList(self):
    """
    Reload the installed images list from disk, discarding the current in-memory version.
    """
    self.clear()

    installedImagesPath = self.user.config["installed-images-list"]
    if os.path.exists(installedImagesPath):
      with open(installedImagesPath, 'r') as file_f:
        try:
          installedImagesDict = json.load(file_f, object_pairs_hook=OrderedDict)
        except ValueError:
          sys.exit("Error:  installed-images.json is not a valid JSON file. Perhaps it is corrupted.")
    else:
      installedImagesDict = OrderedDict()
    # Create the InstalledImage objects.
    for imageId,imageAttributes in installedImagesDict.items():
      try:
        imageSourceHash = imageAttributes["image-source-hash"]
      except KeyError:
        imageSourceHash = ""
      image = InstalledImage(
        user=self.user,
        imageId=imageId,
        imageSourceName=imageAttributes["image-source"],
        sourceRepoId=imageAttributes["source-repo"],
        imageSourceHash=imageSourceHash)
      self[imageId]=image

  def serializeToDict(self):
    # Build a dictionary of installed images.
    installedImagesDict = OrderedDict()
    for _,installedImage in self.items():
      installedImagesDict[installedImage.imageId] = installedImage.serializeToDict()
    return installedImagesDict

  def save(self):
    """
    Save attributes of the installed images to disk.
    """
    if not self.user._has_lock:
      sys.exit("Programmer error. Saving installed images list without first aquiring lock! Please report this incident to: https://github.com/subuser-security/subuser/issues")
    # Write that dictionary to disk.
    installedImagesPath = self.user.config["installed-images-list"]
    with self.user.endUser.get_file(installedImagesPath, 'w') as file_f:
      json.dump(self.serializeToDict(), file_f, indent=1, separators=(',', ': '))

  def unregisterNonExistantImages(self):
    """
    Go through the installed images list and unregister any images that aren't actually installed.
    """
    keysToDelete = []
    for imageId,image in self.items():
      if not image.isDockerImageThere():
        keysToDelete.append(imageId)
    for key in keysToDelete:
      del self[key]
