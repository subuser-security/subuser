#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import os,json,collections
#internal imports
import subuserlib.classes.fileBackedObject, subuserlib.classes.userOwnedObject, subuserlib.classes.subuser, subuserlib.classes.programSource

class Subusers(dict,subuserlib.classes.userOwnedObject.UserOwnedObject,subuserlib.classes.fileBackedObject.FileBackedObject):
  """
  A subusers object stores the set of all subusers owned by a given user.

  >>> import subuserlib.classes.user
  >>> import subuserlib.classes.subusers
  >>> u = subuserlib.classes.user.User()
  >>> subusers = u.getRegistry().getSubusers()
  >>> subusers["foo"].getName()
  u'foo'
  """

  def save(self):
    """
     Save the list of subusers to disk.
    """
    serializedSubusersDict = {}
    for subuserName,subuser in self.iteritems():
      serializedSubusersDict[subuserName]["source-repo"] = subuser.getProgramSource().getRepository().getName()
      serializedSubusersDict[subuserName]["source-program"] = subuser.getProgramSource().getName()
      serializedSubusersDict[subuserName]["executable-shortcut-installed"] = subuser.getProgramSource().isExectableShortcutInstalled()
    with open(os.path.join(self.getUser().getConfig().getSubusersDotJsonPath()), 'w') as file_f:
      json.dump(serializedSubusersDict, file_f, indent=1, separators=(',', ': '))

  def __init__(self,user):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)

    if os.path.exists(self.getUser().getConfig().getSubusersDotJsonPath()):
      with open(self.getUser().getConfig().getSubusersDotJsonPath(), 'r') as file_f:
        serializedSubusersDict = json.load(file_f, object_pairs_hook=collections.OrderedDict)
    else:
      serializedSubusersDict = {}
    for subuserName, subuserAttributes in serializedSubusersDict.iteritems():
      if not subuserAttributes["source-repo"] in self.getUser().getRegistry().getRepositories():
        sys.exit("ERROR: Registry inconsistent. Subuser "+subuserName+" points to non-existant repository: "+subuserAttributes["source-repo"])
      repo = self.getUser().getRegistry().getRepositories()[subuserAttributes["source-repo"]]
      name = subuserAttributes["source-program"]
      imageId = subuserAttributes["docker-image"]
      executableShortcutInstalled = subuserAttributes["executable-shortcut-installed"]
      programSource = subuserlib.classes.programSource.ProgramSource(user=user,name=name,repo=repo)
      self[subuserName] = subuserlib.classes.subuser.Subuser(user,subuserName,programSource,imageId=imageId,executableShortcutInstalled=executableShortcutInstalled)
