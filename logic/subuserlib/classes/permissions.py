# -*- coding: utf-8 -*-

"""
Each subuser has a set of permissions which specify what parts of the host system it is allowed to access.
"""

#external imports
import collections
import hashlib
import sys
#internal imports
from subuserlib.classes.userOwnedObject import UserOwnedObject
from subuserlib.classes.fileBackedObject import FileBackedObject
import subuserlib.permissions

class Permissions(collections.OrderedDict,UserOwnedObject,FileBackedObject):
  def __init__(self,user,initialPermissions,writePath=None):
    self.writePath = writePath
    UserOwnedObject.__init__(self,user)
    collections.OrderedDict.__init__(self)
    self.update(initialPermissions)

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

  def save(self,_have_lock=False):
    if (not self.user._has_lock) and (not _have_lock):
      sys.exit("Programmer error. Saving permissions without first aquiring lock! Please report this incident to: https://github.com/subuser-security/subuser/issues")
    with self.user.endUser.get_file(self.writePath,'w') as fd:
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
          self.user.registry.log(firstLine)
          for subPermission in subPermissions:
            self.user.registry.log("   * "+subPermission)
        else:
          self.user.registry.log(firstLine + " " + subPermissions[0])
    def areAnyOfThesePermitted(permissions):
      permitted = False
      for permission in permissions:
        if self[permission]:
          permitted = True
      return permitted
    preludeDescriptions = sum([subuserlib.permissions.descriptions[permission](self[permission]) for permission in subuserlib.permissions.levels[0]["permissions"]],[])
    for description in preludeDescriptions:
      self.user.registry.log(" "+description)
    for level in subuserlib.permissions.levels[1:]:
      if areAnyOfThesePermitted(level["permissions"]):
        self.user.registry.log(" "+level["description"])
        describePermissions(level["permissions"])
