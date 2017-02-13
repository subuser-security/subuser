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
    defaults = subuserlib.permissions.getDefaults()
    for permission in permissionsToRemove:
      self[permission] = defaults[permission]
    for permission,value in permissionsToAddOrChange.items():
      self[permission] = value

  def save(self,_have_lock=False):
    if (not self.user._has_lock) and (not _have_lock):
      sys.exit("Programmer error. Saving permissions without first aquiring lock! Please report this incident to: https://github.com/subuser-security/subuser/issues")
    with self.user.endUser.get_file(self.writePath,'w') as fd:
      fd.write(subuserlib.permissions.getJSONString(self))

  @property
  def description(self):
    return subuserlib.permissions.getDescription(self)

  def describe(self):
    self.user.registry.log(self.description)
