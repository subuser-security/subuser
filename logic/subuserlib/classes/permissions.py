#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
Each subuser has a set of permissions which specify what parts of the host system it is allowed to access.
"""

#external imports
import collections,hashlib
#internal imports
from subuserlib.classes.userOwnedObject import UserOwnedObject
from subuserlib.classes.fileBackedObject import FileBackedObject
import subuserlib.permissions


class Permissions(collections.OrderedDict,UserOwnedObject,FileBackedObject):
  def __init__(self,user,initialPermissions,writePath):
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
    hasher.update(subuserlib.permissions.getPermissonsJSONString(self).encode('utf-8'))
    return hasher.hexdigest()

  def applyChanges(self,permissionsToRemove,permissionsToAddOrChange):
    for permission in permissionsToRemove:
      self[permission] = subuserlib.permissions.permissionDefaults[permission]
    for permission,value in permissionsToAddOrChange.items():
      self[permission] = value

  def save(self):
    subuserlib.permissions.setPermissions(self,self.__writePath)

  def describe(self):
    def describePermissions(permissions):
      for permission in permissions:
        subPermissions = subuserlib.permissions.permissionDescriptions[permission](self[permission])
        if not subPermissions:
          continue
        firstLine = "  - " + permission + ":"
        multiline = len(subPermissions) > 1
        if multiline:
          print(firstLine)
          for subPermission in subPermissions:
            print("   * "+subPermission)
        else:
          print(firstLine + " " + subPermissions[0])

    def areAnyOfThesePermitted(permissions):
      permitted = False
      for permission in permissions:
        if self[permission]:
          permitted = True
      return permitted

    preludeDescriptions = sum([subuserlib.permissions.permissionDescriptions[permission](self[permission]) for permission in subuserlib.permissions.permissionsPrelude],[])
    for description in preludeDescriptions:
      print(" "+description)

    if areAnyOfThesePermitted(subuserlib.permissions.conservativePermissions):
      print(" Conservative permissions(These are safe):")
      describePermissions(subuserlib.permissions.conservativePermissions)

    if areAnyOfThesePermitted(subuserlib.permissions.moderatePermissions):
      print(" Moderate permissions(These are probably safe):")
      describePermissions(subuserlib.permissions.moderatePermissions)

    if areAnyOfThesePermitted(subuserlib.permissions.liberalPermissions):
      print(" Liberal permissions(These may pose a security risk):")
      describePermissions(subuserlib.permissions.liberalPermissions)

    if areAnyOfThesePermitted(subuserlib.permissions.anarchisticPermissions):
      print("WARNING: this subuser has full access to your system when run.")
      describePermissions(subuserlib.permissions.anarchisticPermissions)
