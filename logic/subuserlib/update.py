# -*- coding: utf-8 -*-

"""
High level operations used for updating, rolling back, locking ect.
"""

#external imports
import sys
#internal imports
import subuserlib.verify
import subuserlib.subprocessExtras as subprocessExtras

#####################################################################################
def all(user,permissionsAccepter,prompt=False,useCache=False):
  """
  This command updates(if needed) all of the installed subuser images.
  """
  user.getRegistry().log("Updating...")
  for _,repository in user.getRegistry().getRepositories().items():
    repository.updateSources()
  subusers = user.getRegistry().getSubusers().getSortedList()
  subuserlib.verify.verify(user,checkForUpdatesExternally=True,useCache=useCache,subusers=subusers,permissionsAccepter=permissionsAccepter,prompt=prompt)
  user.getRegistry().commit()

def subusers(user,subusers,permissionsAccepter,prompt=False,useCache=False):
  """
  This command updates the specified subusers' images.
  """
  user.getRegistry().log("Updating...")
  for _,repository in user.getRegistry().getRepositories().items():
    repository.updateSources()
  subuserlib.verify.verify(user,subusers=subusers,useCache=useCache,checkForUpdatesExternally=True,permissionsAccepter=permissionsAccepter,prompt=prompt)
  user.getRegistry().commit()

def lockSubuser(user,subuser,commit):
  """
  Lock the subuser to the image and permissions that it had at a given registry commit.
  """
  from subuserlib.classes.registry import Registry
  registryAtOldCommit = Registry(user,gitReadHash=commit)
  if not registryAtOldCommit.getGitRepository().doesCommitExist(commit):
    sys.exit("Commit "+commit+" does not exist. Cannot lock to commit.")
  subuser.getPermissions().save()
  subuser.getPermissionsTemplate().save()
  user.getRegistry().logChange("Locking subuser "+subuser.getName()+" to commit: "+commit)
  subuser.setLocked(True)
  subuserlib.verify.verify(user)
  user.getRegistry().commit()

def unlockSubuser(user,subuser,permissionsAccepter,prompt):
  """
  Unlock the subuser, leaving it to have an up to date image.  Delete user set permissions if unlockPermissions is True.
  """
  if subuser.locked():
    user.getRegistry().logChange("Unlocking subuser "+subuser.getName())
    subuser.setLocked(False)
    subuserlib.verify.verify(user,subusers=[subuser],checkForUpdatesExternally=True,permissionsAccepter=permissionsAccepter,prompt=prompt)
    user.getRegistry().commit()
  else:
    user.getRegistry().log("Subuser "+subuser.getName() + " is not locked. Doing nothing.")
