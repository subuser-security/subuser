#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
This is the list of subusers controled by a given user.
"""

#external imports
import os,json,collections,sys
#internal imports
import subuserlib.classes.fileBackedObject, subuserlib.classes.userOwnedObject, subuserlib.classes.subuser, subuserlib.classes.imageSource

class Subusers(dict,subuserlib.classes.userOwnedObject.UserOwnedObject,subuserlib.classes.fileBackedObject.FileBackedObject):
  """
  A subusers object stores the set of all subusers owned by a given user.

  >>> import subuserlib.classes.user
  >>> import subuserlib.classes.subusers
  >>> import subuserlib.subuser
  >>> u = subuserlib.classes.user.User()
  >>> subuserlib.subuser.add(u,"foo","foo@default")
  Initial commit.
  Adding subuser foo foo@default
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Installing foo ...
  Installed new image for subuser foo
  Running garbage collector on temporary repositories...
  >>> subusers = u.getRegistry().getSubusers()
  >>> subusers["foo"].getName()
  'foo'
  """

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
      if subuser.locked():
        serializedLockedSubusersDict[subuserName] = serializedSubuser
      else:
        serializedUnlockedSubusersDict[subuserName] = serializedSubuser
    with open(os.path.join(self.getUser().getConfig().getSubusersDotJsonPath()), 'w') as file_f:
      json.dump(serializedUnlockedSubusersDict, file_f, indent=1, separators=(',', ': '))
    with open(os.path.join(self.getUser().getConfig().getLockedSubusersDotJsonPath()), 'w') as file_f:
      json.dump(serializedLockedSubusersDict, file_f, indent=1, separators=(',', ': '))

  def _loadSerializedSubusersDict(self,serializedSubusersPath,locked):
    """
    Load the serialzed subusers json file into memory.
    """
    serializedSubusersDict = {}
    if os.path.exists(serializedSubusersPath):
      with open(serializedSubusersPath, 'r') as file_f:
        serializedSubusersDict.update(json.load(file_f, object_pairs_hook=collections.OrderedDict))

    for subuserName, subuserAttributes in serializedSubusersDict.items():
      if not subuserAttributes["source-repo"] in self.getUser().getRegistry().getRepositories():
        sys.exit("ERROR: Registry inconsistent. Subuser "+str(subuserName)+" points to non-existant repository: "+str(subuserAttributes["source-repo"]))
      repo = self.getUser().getRegistry().getRepositories()[subuserAttributes["source-repo"]]
      name = subuserAttributes["image-source"]
      if "docker-image" in subuserAttributes:
        imageId = subuserAttributes["docker-image"]
      else:
        imageId = None
      executableShortcutInstalled = subuserAttributes["executable-shortcut-installed"]
      imageSource = subuserlib.classes.imageSource.ImageSource(user=self.getUser(),name=name,repo=repo)
      self[subuserName] = subuserlib.classes.subuser.Subuser(self.getUser(),subuserName,imageSource,imageId=imageId,executableShortcutInstalled=executableShortcutInstalled,locked=locked)

  def __init__(self,user):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self._loadSerializedSubusersDict(self.getUser().getConfig().getLockedSubusersDotJsonPath(),locked=True)
    self._loadSerializedSubusersDict(self.getUser().getConfig().getSubusersDotJsonPath(),locked=False)

