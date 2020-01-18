# -*- coding: utf-8 -*-

"""
This is the set of broken images that belong to a given user.
"""

#external imports
import os
import json
from collections import OrderedDict
import sys
#internal imports
from subuserlib.classes.fileBackedObject import FileBackedObject
from subuserlib.classes.userOwnedObject import UserOwnedObject

class BrokenImages(UserOwnedObject,FileBackedObject):
  def __init__(self,user):
    UserOwnedObject.__init__(self,user)
    self.images = []
    self.reloadBrokenImagesList()

  def reloadBrokenImagesList(self):
    """
    Reload the broken images list from disk, discarding the current in-memory version.
    """
    self.images = []

    brokenImagesPath = self.user.config["broken-images-list"]
    if os.path.exists(brokenImagesPath):
      with open(brokenImagesPath, 'r') as file_f:
        try:
          self.images = json.load(file_f, object_pairs_hook=OrderedDict)
        except ValueError:
          sys.exit("Error:  "+brokenImagesPath+" is not a valid JSON file. Perhaps it is corrupted.")

  def save(self):
    """
    Save attributes of the broken images to disk.
    """
    if not self.user._has_lock:
      sys.exit("Programmer error. Saving broken images list without first aquiring lock! Please report this incident to: https://github.com/subuser-security/subuser/issues")
    # Write that dictionary to disk.
    brokenImagesPath = self.user.config["broken-images-list"]
    with self.user.endUser.get_file(brokenImagesPath, 'w') as file_f:
      json.dump(self.images, file_f, indent=1, separators=(',', ': '))
