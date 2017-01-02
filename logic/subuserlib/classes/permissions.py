# -*- coding: utf-8 -*-

"""
Each subuser has a set of permissions which specify what parts of the host system it is allowed to access.
"""

#external imports
import collections
import hashlib
#internal imports
from subuserlib.classes.userOwnedObject import UserOwnedObject
from subuserlib.classes.fileBackedObject import FileBackedObject
import subuserlib.permissions

class Permissions(collections.OrderedDict,UserOwnedObject,FileBackedObject):
  def __init__(self,user,initialPermissions,writePath=None):
    self.__writePath = writePath
    UserOwnedObject.__init__(self,user)
    collections.OrderedDict.__init__(self)
    self.update(initialPermissions)

  def getWritePath(self):
    """
    Return the path to which the permissions object is to be saved.
    """
    return self.__writePath

  def getHash(self):
    """
    Return the SHA512 hash of the given permissions.
    """
    hasher = hashlib.sha512()
    hasher.update(subuserlib.permissions.getJSONString(self).encode('utf-8'))
    return hasher.hexdigest()

  def applyChanges(self,permissionsToRemove,permissionsToAddOrChange):
    for permission in permissionsToRemove:
      self[permission] = subuserlib.permissions.defaults[permission]
    for permission,value in permissionsToAddOrChange.items():
      self[permission] = value

  def save(self):
    with self.getUser().getEndUser().get_file(self.__writePath,'w') as fd:
      fd.write(subuserlib.permissions.getJSONString(self))

  def describe(self):
    def describePermissions(permissions):
      for permission in permissions:
        subPermissions = subuserlib.permissions.descriptions[permission](self[permission])
        if not subPermissions:
          continue
        firstLine = "  - " + permission + ":"
        multiline = len(subPermissions) > 1
        if multiline:
          self.getUser().getRegistry().log(firstLine)
          for subPermission in subPermissions:
            self.getUser().getRegistry().log("   * "+subPermission)
        else:
          self.getUser().getRegistry().log(firstLine + " " + subPermissions[0])
    def areAnyOfThesePermitted(permissions):
      permitted = False
      for permission in permissions:
        if self[permission]:
          permitted = True
      return permitted
    preludeDescriptions = sum([subuserlib.permissions.descriptions[permission](self[permission]) for permission in subuserlib.permissions.levels[0]["permissions"]],[])
    for description in preludeDescriptions:
      self.getUser().getRegistry().log(" "+description)
    for level in subuserlib.permissions.levels[1:]:
      if areAnyOfThesePermitted(level["permissions"]):
        self.getUser().getRegistry().log(" "+level["description"])
        describePermissions(level["permissions"])
