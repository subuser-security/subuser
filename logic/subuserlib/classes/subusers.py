# -*- coding: utf-8 -*-

"""
This is the list of subusers controlled by a given user.
"""

#external imports
import os
import json
import collections
import sys
#internal imports
from subuserlib.classes.fileBackedObject import FileBackedObject
from subuserlib.classes.userOwnedObject import UserOwnedObject
from subuserlib.classes.subuser import Subuser
import subuserlib.classes.imageSource

class Subusers(dict,UserOwnedObject,FileBackedObject):
  """
  A subusers object stores the set of all subusers owned by a given user.

  >>> import subuserlib.classes.user
  >>> import subuserlib.classes.subusers
  >>> import subuserlib.subuser
  >>> from subuserlib.classes.permissionsAccepters.acceptPermissionsAtCLI import AcceptPermissionsAtCLI
  >>> u = subuserlib.classes.user.User()
  >>> permissionsAccepter = AcceptPermissionsAtCLI(u,alwaysAccept=True)

  >>> subuserlib.subuser.add(u,"foo","foo@default",permissionsAccepter)
  Adding subuser foo foo@default
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  foo would like to have the following permissions:
   Description:
   Maintainer:
   Executable: /usr/bin/foo
  A - Accept and apply changes
  E - Apply changes and edit result
  A
  Checking if images need to be updated or installed...
  Checking if subuser foo is up to date.
  New images for the following subusers need to be installed:
  foo
  Installing foo ...
  Building...
  Building...
  Building...
  Successfully built 1
  Building...
  Building...
  Building...
  Successfully built 2
  Installed new image <2> for subuser foo
  Running garbage collector on temporary repositories...
  >>> subusers = u.getRegistry().getSubusers()
  >>> subusers["foo"].getName()
  'foo'
  """
  def __init__(self,user):
    UserOwnedObject.__init__(self,user)
    if os.path.exists(self.getUser().getConfig()["locked-subusers-path"]):
      with open(self.getUser().getConfig()["locked-subusers-path"],"r") as fileHandle:
        self._loadSerializedSubusersDict(json.load(fileHandle, object_pairs_hook=collections.OrderedDict),locked=True)
    registryFileStructure = self.getUser().getRegistry().getGitRepository().getFileStructureAtCommit(self.getUser().getRegistry().getGitReadHash())
    if self.getUser().getRegistry().initialized and "subusers.json" in registryFileStructure.lsFiles("./"):
      serializedUnlockedSubusersDict = json.loads(registryFileStructure.read("subusers.json"), object_pairs_hook=collections.OrderedDict)
      self._loadSerializedSubusersDict(serializedUnlockedSubusersDict,locked=False)

  def serializeToDict(self):
    serializedDict=collections.OrderedDict()
    serializedDict["locked"]=collections.OrderedDict()
    serializedDict["unlocked"]=collections.OrderedDict()
    for subuserName,subuser in self.items():
      serializedSubuser = collections.OrderedDict()
      serializedSubuser["source-repo"] = subuser.getSourceRepoName()
      serializedSubuser["image-source"] = subuser.getImageSourceName()
      serializedSubuser["executable-shortcut-installed"] = subuser.isExecutableShortcutInstalled()
      serializedSubuser["docker-image"] = subuser.getImageId()
      serializedSubuser["service-subusers"] = subuser.getServiceSubuserNames()
      if subuser.locked():
        serializedDict["locked"][subuserName] = serializedSubuser
      else:
        serializedDict["unlocked"][subuserName] = serializedSubuser
    return serializedDict

  def save(self):
    """
    Save the list of subusers to disk.
    """
    serializedDict = self.serializeToDict()
    with open(os.path.join(self.getUser().getConfig()["registry-dir"],"subusers.json"), 'w') as file_f:
      json.dump(serializedDict["unlocked"], file_f, indent=1, separators=(',', ': '))
    with open(os.path.join(self.getUser().getConfig()["locked-subusers-path"]), 'w') as file_f:
      json.dump(serializedDict["locked"], file_f, indent=1, separators=(',', ': '))

  def _loadSerializedSubusersDict(self,serializedSubusersDict,locked):
    """
    Load the serialized subusers json file into memory.
    """
    for subuserName, subuserAttributes in serializedSubusersDict.items():
      repoName = subuserAttributes["source-repo"]
      imageSourceName = subuserAttributes["image-source"]
      if "docker-image" in subuserAttributes:
        imageId = subuserAttributes["docker-image"]
      else:
        imageId = None
      if "service-subusers" in subuserAttributes:
        serviceSubusers = subuserAttributes["service-subusers"]
      else:
        serviceSubusers = []
      executableShortcutInstalled = subuserAttributes["executable-shortcut-installed"]
      self[subuserName] = Subuser(self.getUser(),subuserName,imageSourceName=imageSourceName,repoName=repoName,imageId=imageId,executableShortcutInstalled=executableShortcutInstalled,locked=locked,serviceSubusers=serviceSubusers)

  def getSortedList(self):
    """
    Return a list of subusers sorted by name.
    """
    return list(sorted(self.values(),key=lambda subuser:subuser.getName()))
