#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
"""
High level operations used for updating, rolling back, locking ect.
"""

#external imports
#import ..
#internal imports
import subuserlib.verify,subuserlib.git,subuserlib.subprocessExtras

#####################################################################################
def updateAll(user):
  """
  This command updates all or some of the installed subuser images.
  """
  user.getRegistry().log("Updating...")
  for _,repository in user.getRegistry().getRepositories().items():
    repository.updateSources()
  subuserlib.verify.verify(user)
  user.getRegistry().commit()

def showLog(user):
  subuserlib.git.runGit(["log"],cwd=user.getConfig().getRegistryPath())

def checkoutNoCommit(user,commit):
  subuserlib.subprocessExtras.subprocessCheckedCall(["rm","-rf","*"],cwd=user.getConfig().getRegistryPath())
  subuserlib.git.runGit(["checkout",commit,"."],cwd=user.getConfig().getRegistryPath())
  user.getRegistry().getRepositories().reloadRepositoryLists()

def rollback(user,commit):
  user.getRegistry().logChange("Rolling back to commit: "+commit)
  checkoutNoCommit(user,commit)
  subuserlib.verify.verify(user)
  user.getRegistry().commit()

def lockSubuser(user,subuserName,commit):
  """
  Lock the subuser to the image and permissions that it had at a given registry commit.
  """

def unlockSubuser(user,subuserName,unlockPermissions=False):
  """
  Unlock the subuser, leaving it to have an up to date image.  Delete user set permissions if unlockPermissions is True.
  """
