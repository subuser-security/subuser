#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
"""
High level operations used for updating, rolling back, locking ect.
"""

#external imports
import os
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
  subuserlib.verify.verify(user,checkForUpdatesExternally=True)
  user.getRegistry().commit()

def showLog(user):
  subuserlib.git.runGit(["log"],cwd=user.getConfig()["registry-dir"])

def checkoutNoCommit(user,commit):
  subuserlib.subprocessExtras.subprocessCheckedCall(["rm","-rf","*"],cwd=user.getConfig()["registry-dir"])
  subuserlib.git.runGit(["checkout",commit,"."],cwd=user.getConfig()["registry-dir"])
  user.reloadRegistry()

def rollback(user,commit):
  checkoutNoCommit(user,commit)
  user.getRegistry().logChange("Rolling back to commit: "+commit)
  subuserlib.verify.verify(user)
  user.getRegistry().commit()

def lockSubuser(user,subuserName,commit):
  """
  Lock the subuser to the image and permissions that it had at a given registry commit.
  """
  checkoutNoCommit(user,commit)
  subuserObject = user.getRegistry().getSubusers()[subuserName]
  if not os.path.exists(os.path.join(user.getConfig()["user-set-permissions-dir"],subuserName,"permissions.json")):
    subuserObject.getPermissions().save()
  checkoutNoCommit(user,"master")
  user.getRegistry().logChange("Locking subuser "+subuserName+" to commit: "+commit)
  user.getRegistry().getSubusers()[subuserName] = subuserObject
  subuserObject.setLocked(True)
  subuserlib.verify.verify(user)
  user.getRegistry().commit()

def unlockSubuser(user,subuserName):
  """
  Unlock the subuser, leaving it to have an up to date image.  Delete user set permissions if unlockPermissions is True.
  """
  user.getRegistry().logChange("Unlocking subuser "+subuserName)
  user.getRegistry().getSubusers()[subuserName].setLocked(False)
  subuserlib.verify.verify(user)
  user.getRegistry().commit()
 
