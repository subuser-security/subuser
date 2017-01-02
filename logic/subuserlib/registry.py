# -*- coding: utf-8 -*-

"""
High level operations used for interacting with the subuser registry.
"""

#external imports
#import ...
#internal imports
import subuserlib.verify

def showLog(user):
  user.getRegistry().getGitRepository().runShowOutput(["log"])

def checkoutNoCommit(user,commit):
  user.getEndUser().call(["rm","-rf","*"],cwd=user.getConfig()["registry-dir"])
  user.getRegistry().getGitRepository().run(["checkout",commit,"."])
  user.reloadRegistry()

def rollback(user,commit):
  checkoutNoCommit(user,commit)
  user.getRegistry().logChange("Rolling back to commit: "+commit)
  subuserlib.verify.verify(user)
  user.getRegistry().commit()
