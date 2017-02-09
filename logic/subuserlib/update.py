# -*- coding: utf-8 -*-

"""
High level operations used for updating, rolling back, locking ect.
"""

#external imports
import sys
#internal imports
import subuserlib.verify

#####################################################################################
def all(user,permissionsAccepter,prompt=False,useCache=False):
  """
  This command updates(if needed) all of the installed subuser images.
  """
  user.registry.log("Updating...")
  for _,repository in user.registry.repositories.items():
    repository.updateSources()
  subusers = user.registry.subusers.getSortedList()
  subuserlib.verify.verify(user,checkForUpdatesExternally=True,useCache=useCache,subusers=subusers,permissionsAccepter=permissionsAccepter,prompt=prompt)
  user.registry.commit()

def subusers(user,subusers,permissionsAccepter,prompt=False,useCache=False):
  """
  This command updates the specified subusers' images.
  """
  user.registry.log("Updating...")
  for _,repository in user.registry.repositories.items():
    repository.updateSources()
  subuserlib.verify.verify(user,subusers=subusers,useCache=useCache,checkForUpdatesExternally=True,permissionsAccepter=permissionsAccepter,prompt=prompt)
  user.registry.commit()

def lockSubuser(user,subuser,commit):
  """
  Lock the subuser to the image and permissions that it had at a given registry commit.
  """
  from subuserlib.classes.user import User
  from subuserlib.classes.registry import Registry
  oldUser = User(name=user.name,homeDir=user.homeDir)
  oldUser.registry = Registry(oldUser,gitReadHash=commit,ignoreVersionLocks=True,initialized=True)
  if not oldUser.registry.gitRepository.doesCommitExist(commit):
    sys.exit("Commit "+commit+" does not exist. Cannot lock to commit.")
  try:
    oldSubuser = oldUser.registry.subusers[subuser.name]
  except KeyError:
    sys.exit("Subuser, "+subuser.name+" did not exist yet at commit "+commit+". Cannot lock to commit.")
  subuser.imageId = oldSubuser.imageId
  oldSubuser.permissions.save(_have_lock=True)
  oldSubuser.getPermissionsTemplate().save(_have_lock=True)
  user.registry.logChange("Locking subuser "+subuser.name+" to commit: "+commit)
  user.registry.logChange("New image id is "+subuser.imageId)
  subuser.locked = True
  subuserlib.verify.verify(user)
  user.registry.commit()

def unlockSubuser(user,subuser,permissionsAccepter,prompt):
  """
  Unlock the subuser, leaving it to have an up to date image.  Delete user set permissions if unlockPermissions is True.
  """
  if subuser.locked:
    user.registry.logChange("Unlocking subuser "+subuser.name)
    subuser.locked = False
    subuserlib.verify.verify(user,subusers=[subuser],checkForUpdatesExternally=True,permissionsAccepter=permissionsAccepter,prompt=prompt)
    user.registry.commit()
  else:
    user.registry.log("Subuser "+subuser.name + " is not locked. Doing nothing.")
