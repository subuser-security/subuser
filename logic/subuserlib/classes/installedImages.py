# -*- coding: utf-8 -*-

"""
This is the set of installed images that bellongs to a given user.
"""

#external imports
import os
import json
import collections
import sys
#internal imports
from subuserlib.classes.installedImage import InstalledImage
from subuserlib.classes.fileBackedObject import FileBackedObject
from subuserlib.classes.userOwnedObject import UserOwnedObject

class InstalledImages(dict,UserOwnedObject,FileBackedObject):
  def __init__(self,user):
    UserOwnedObject.__init__(self,user)
    self.reloadInstalledImagesList()

  def reloadInstalledImagesList(self):
    """
    Reload the installed images list from disk, discarding the current in-memory version.
    """
    self.clear()

    installedImagesPath = self.getUser().getConfig()["installed-images-list"]
    if os.path.exists(installedImagesPath):
      with open(installedImagesPath, 'r') as file_f:
        try:
          installedImagesDict = json.load(file_f, object_pairs_hook=collections.OrderedDict)
        except ValueError:
          sys.exit("Error:  installed-images.json is not a valid JSON file. Perhaps it is corrupted.")
    else:
      installedImagesDict = {}
    # Create the InstalledImage objects.
    for imageId,imageAttributes in installedImagesDict.items():
      try:
        imageSourceHash = imageAttributes["image-source-hash"]
      except KeyError:
        imageSourceHash = ""
      image = InstalledImage(
        user=self.getUser(),
        imageId=imageId,
        imageSourceName=imageAttributes["image-source"],
        sourceRepoId=imageAttributes["source-repo"],
        imageSourceHash=imageSourceHash)
      self[imageId]=image

  def serializeToDict(self):
    # Build a dictionary of installed images.
    installedImagesDict = {}
    for _,installedImage in self.items():
      imageAttributes = {}
      imageAttributes["image-source-hash"] = installedImage.getImageSourceHash()
      imageAttributes["image-source"] = installedImage.getImageSourceName()
      imageAttributes["source-repo"] = installedImage.getSourceRepoId()
      installedImagesDict[installedImage.getImageId()] = imageAttributes
    return installedImagesDict

  def save(self):
    """
    Save attributes of the installed images to disk.
    """
    # Write that dictionary to disk.
    installedImagesPath = self.getUser().getConfig()["installed-images-list"]
    with self.getUser().getEndUser().get_file(installedImagesPath, 'w') as file_f:
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
