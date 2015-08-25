#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

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
    if "subusers.json" in registryFileStructure.lsFiles("./"):
      serializedUnlockedSubusersDict = json.loads(registryFileStructure.read("subusers.json"), object_pairs_hook=collections.OrderedDict)
      self._loadSerializedSubusersDict(serializedUnlockedSubusersDict,locked=False)

  def save(self):
    """
    Save the list of subusers to disk.
    """
    serializedUnlockedSubusersDict = {}
    serializedLockedSubusersDict = {}
    for subuserName,subuser in self.items():
      serializedSubuser = {}
      serializedSubuser["source-repo"] = subuser.getImageSource().getRepository().getName()
      serializedSubuser["image-source"] = subuser.getImageSource().getName()
      serializedSubuser["executable-shortcut-installed"] = subuser.isExecutableShortcutInstalled()
      serializedSubuser["docker-image"] = subuser.getImageId()
      serializedSubuser["service-subusers"] = subuser.getServiceSubuserNames()
      if subuser.locked():
        serializedLockedSubusersDict[subuserName] = serializedSubuser
      else:
        serializedUnlockedSubusersDict[subuserName] = serializedSubuser
    with open(os.path.join(self.getUser().getConfig()["registry-dir"],"subusers.json"), 'w') as file_f:
      json.dump(serializedUnlockedSubusersDict, file_f, indent=1, separators=(',', ': '))
    with open(os.path.join(self.getUser().getConfig()["locked-subusers-path"]), 'w') as file_f:
      json.dump(serializedLockedSubusersDict, file_f, indent=1, separators=(',', ': '))

  def _loadSerializedSubusersDict(self,serializedSubusersDict,locked):
    """
    Load the serialzed subusers json file into memory.
    """
    for subuserName, subuserAttributes in serializedSubusersDict.items():
      if not subuserAttributes["source-repo"] in self.getUser().getRegistry().getRepositories():
        sys.exit("ERROR: Registry inconsistent. Subuser "+str(subuserName)+" points to non-existant repository: "+str(subuserAttributes["source-repo"]))
      repo = self.getUser().getRegistry().getRepositories()[subuserAttributes["source-repo"]]
      name = subuserAttributes["image-source"]
      if "docker-image" in subuserAttributes:
        imageId = subuserAttributes["docker-image"]
      else:
        imageId = None
      if "service-subusers" in subuserAttributes:
        serviceSubusers = subuserAttributes["service-subusers"]
      else:
        serviceSubusers = []
      executableShortcutInstalled = subuserAttributes["executable-shortcut-installed"]
      imageSource = subuserlib.classes.imageSource.ImageSource(user=self.getUser(),name=name,repo=repo)
      self[subuserName] = Subuser(self.getUser(),subuserName,imageSource,imageId=imageId,executableShortcutInstalled=executableShortcutInstalled,locked=locked,serviceSubusers=serviceSubusers)
