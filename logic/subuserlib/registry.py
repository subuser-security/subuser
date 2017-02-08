# -*- coding: utf-8 -*-

"""
High level operations used for interacting with the subuser registry.
"""

#external imports
#import ...
#internal imports
import subuserlib.verify

def showLog(user):
  user.registry.gitRepository.runShowOutput(["log"])

def checkoutNoCommit(user,commit):
  user.endUser.call(["rm","-rf","*"],cwd=user.config["registry-dir"])
  user.registry.gitRepository.run(["checkout",commit,"."])
  user.reloadRegistry()

def rollback(user,commit):
  checkoutNoCommit(user,commit)
  user.registry.logChange("Rolling back to commit: "+commit)
  subuserlib.verify.verify(user)
  user.registry.commit()
