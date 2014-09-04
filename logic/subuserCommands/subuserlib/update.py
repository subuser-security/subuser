#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

# This command updates all or some of the installed subuser programs.

#external imports
#import ..
#internal imports
import subuserlib.verify,subuserlib.git,subuserlib.subprocessExtras

#####################################################################################
def updateAll(user):
  user.getRegistry().log("Updating...")
  for _,repository in user.getRegistry().getRepositories().iteritems():
    repository.updateSources()
  subuserlib.verify.verify(user)
  user.getRegistry().commit()

def showLog(user):
  subuserlib.git.runGit(["log"],cwd=user.getConfig().getRegistryPath())

def checkoutNoCommit(user,commit):
  exit()
  subuserlib.subprocessExtras.subprocessCheckedCall(["rm","-rf","*"],cwd=user.getConfig().getRegistryPath())
  subuserlib.git.runGit(["checkout",commit,"."],cwd=user.getConfig().getRegistryPath())
  user.getRegistry().getRepositories().reloadRepositoryLists()

def checkout(user,commit):
  user.getRegistry().logChange("Rolling back to commit: "+args[1])
  checkoutNoCommit(user,commit)
  subuserlib.verify.verify(user)
  user.getRegistry().commit()

