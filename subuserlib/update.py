# -*- coding: utf-8 -*-

"""
High level operations used for updating, rolling back, locking ect.
"""

#external imports
import sys
#internal imports
import subuserlib.verify

#####################################################################################
def run(operation):
  """
  This command updates(if needed) all of the installed subuser images.
  """
  operation.user.registry.log("Updating...")
  for _,repository in operation.user.registry.repositories.items():
    repository.updateSources()
  subuserlib.verify.verify(operation)
  operation.user.registry.commit()

def lockSubusers(operation,commit):
  """
  Lock the subusers to the images and permissions they had at a given registry commit.
  """
  user = operation.user
  from subuserlib.classes.user import User
  from subuserlib.classes.registry import Registry
  oldUser = User(name=user.name,homeDir=user.homeDir)
  oldUser.registry = Registry(oldUser,gitReadHash=commit,ignoreVersionLocks=True,initialized=True)
  if not oldUser.registry.gitRepository.doesCommitExist(commit):
    sys.exit("Commit "+commit+" does not exist. Cannot lock to commit.")
  oldSubusers = []
  for subuser in operation.subusers:
    try:
      oldSubusers.append((subuser, oldUser.registry.subusers[subuser.name]))
    except KeyError:
      sys.exit("Subuser, "+subuser.name+" did not exist yet at commit "+commit+". Cannot lock to commit.")
  for (subuser, oldSubuser) in oldSubusers:
    subuser.imageId = oldSubuser.imageId
    oldSubuser.permissions.save(_have_lock=True)
    oldSubuser.getPermissionsTemplate().save(_have_lock=True)
    subuser.locked = True
    user.registry.logChange("Locking subuser "+subuser.name+" to commit: "+commit)
    user.registry.logChange("New image id is "+subuser.imageId)
  subuserlib.verify.verify(user.operation)
  user.registry.commit()

def unlockSubusers(operation):
  """
  Unlock the subuser, leaving it to have an up to date image.  Delete user set permissions if unlockPermissions is True.
  """
  user = operation.user
  subusersToUnlock = []
  for subuser in operation.subusers:
    if subuser.locked:
      subusersToUnlock.append(subuser)
      user.registry.logChange("Unlocking subuser "+subuser.name)
      subuser.locked = False
  operation.subusers = subusersToUnlock
  if operation.subusers:
    user.operation.checkForUpdatesExternaly=True
    subuserlib.verify.verify(operation)
    user.registry.commit()
  else:
    user.registry.log("Subuser "+subuser.name + " is not locked. Doing nothing.")
