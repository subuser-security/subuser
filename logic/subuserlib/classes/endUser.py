# -*- coding: utf-8 -*-

"""
The ``EndUser`` object the object that represents the user account owned by the human user of the system. It is possible to run subuser using a different user account, in order to isolate root from the end user's user account.
"""
#external imports
import getpass
import os
import sys
import pwd
#internal imports
from subuserlib import test
from subuserlib import paths
from subuserlib.classes.userOwnedObject import UserOwnedObject

class EndUser(UserOwnedObject,object):
  def __init__(self,user):
    UserOwnedObject.__init__(self,user)
    self.proxiedByOtherUser = False
    try:
      self.name = self.getUser().getConfig()["user"]
      self.proxiedByOtherUser = True
    except KeyError:
      try:
        self.name = getpass.getuser()
      except KeyError:
        # We use a broken setup when generating documentation...
        self.name = "I have no name!"
    self.uid = 1000
    self.gid = 1000
    if not test.testing:
      try:
        self.uid = pwd.getpwnam(self.name)[2]
        self.gid = pwd.getpwnam(self.name)[3]
      except KeyError:
        pass
    if not self.uid == 0:
      self.homeDir = os.path.join("/home/",self.name)
    else:
      self.homeDir = "/root/"

  def chown(self,path):
    """
    Make this user own the given file if subuser is running as root.
    """
    if self.proxiedByOtherUser:
      os.chown(path,self.uid,self.gid)

  def makedirs(self,path):
    """
    Create directory + parents, if the directory does not yet exist. Newly created directories will be owned by the user.
    """
    # Taken from http://stackoverflow.com/questions/3167154/how-to-split-a-dos-path-into-its-components-in-python
    folders = []
    path = os.path.realpath(path)
    while 1:
      path, folder = os.path.split(path)
      if folder:
        folders.append(folder)
      else:
        if path:
          folders.append(path)
        break
    pathBeingBuilt = "/"
    for folder in reversed(folders):
      pathBeingBuilt = os.path.join(pathBeingBuilt,folder)
      if not os.path.exists(pathBeingBuilt):
        os.mkdir(pathBeingBuilt)
        self.chown(pathBeingBuilt)

  def getSudoArgs(self):
    if self.proxiedByOtherUser:
      return ["sudo","--user",self.name]
    else:
      return []
