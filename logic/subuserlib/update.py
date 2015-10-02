#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
High level operations used for updating, rolling back, locking ect.
"""

#external imports
#import ...
#internal imports
import subuserlib.verify
import subuserlib.subprocessExtras as subprocessExtras

#####################################################################################
def all(user,permissionsAccepter):
  """
  This command updates(if needed) all of the installed subuser images.
  """
  user.getRegistry().log("Updating...")
  for _,repository in user.getRegistry().getRepositories().items():
    repository.updateSources()
  subuserNames = list(user.getRegistry().getSubusers().keys())
  subuserNames.sort()
  subuserlib.verify.verify(user,checkForUpdatesExternally=True,subuserNames=subuserNames,permissionsAccepter=permissionsAccepter)
  user.getRegistry().commit()

def subusers(user,subuserNames,permissionsAccepter):
  """
  This command updates the specified subusers' images.
  """
  user.getRegistry().log("Updating...")
  for _,repository in user.getRegistry().getRepositories().items():
    repository.updateSources()
  subuserlib.verify.verify(user,subuserNames=subuserNames,checkForUpdatesExternally=True,permissionsAccepter=permissionsAccepter)
  user.getRegistry().commit()

def lockSubuser(user,subuserName,commit):
  """
  Lock the subuser to the image and permissions that it had at a given registry commit.
  """
  from subuserlib.classes.registry import Registry
  registryAtOldCommit = Registry(user,gitReadHash=commit)
  subuserObject = registryAtOldCommit.getSubusers()[subuserName]
  subuserObject.getPermissions().save()
  subuserObject.getPermissionsTemplate().save()
  user.getRegistry().logChange("Locking subuser "+subuserName+" to commit: "+commit)
  user.getRegistry().getSubusers()[subuserName] = subuserObject
  subuserObject.setLocked(True)
  subuserlib.verify.verify(user)
  user.getRegistry().commit()

def unlockSubuser(user,subuserName,permissionsAccepter):
  """
  Unlock the subuser, leaving it to have an up to date image.  Delete user set permissions if unlockPermissions is True.
  """
  user.getRegistry().logChange("Unlocking subuser "+subuserName)
  user.getRegistry().getSubusers()[subuserName].setLocked(False)
  subuserlib.verify.verify(user,subuserNames=[subuserName],checkForUpdatesExternally=True,permissionsAccepter=permissionsAccepter)
  user.getRegistry().commit()
