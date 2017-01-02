# -*- coding: utf-8 -*-

"""
The ``EndUser`` object the object that represents the user account owned by the human user of the system. It is possible to run subuser using a different user account, in order to isolate root from the end user's user account.
"""
#external imports
import getpass
import os
import sys
import pwd
import subprocess
#internal imports
from subuserlib import test
from subuserlib import paths
from subuserlib.classes.userOwnedObject import UserOwnedObject

class EndUser(UserOwnedObject,object):
  def __init__(self,user,name=None):
    UserOwnedObject.__init__(self,user)
    self.proxiedByOtherUser = False
    self.sudo = False
    self.name = name
    try:
      self.name = self.getUser().getConfig()["user"]
      self.proxiedByOtherUser = True
    except KeyError:
      try:
        self.name = os.environ["SUDO_USER"]
        self.sudo = True
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
      if self.sudo:
        self.uid = int(os.environ.get('SUDO_UID'))
        self.gid = int(os.environ.get('SUDO_GID'))
      else:
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

  #Thanks http://stackoverflow.com/questions/25791311/creating-a-file-with-python-using-sudo-makes-its-owner-root
  def create_file(self,path):
    #create containing folder
    directory,_ = os.path.split(path)
    self.makedirs(directory)
    #create file normally
    open(path, 'a').close()
    # then fix the ownership
    self.chown(path)

  def get_file(self,path, mode="a+"):
    """Create a file if it does not exists, fix ownership and return it open"""
    self.create_file(path)
    # open the file and return it
    return open(path, mode)

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
        self.mkdir(pathBeingBuilt)

  def mkdir(self,path):
    os.mkdir(path)
    self.chown(path)

  def getSudoArgs(self):
    if self.proxiedByOtherUser:
      return ["sudo","--user",self.name]
    else:
      return []

  def call(self,command,cwd=None):
    process = subprocess.Popen(self.getSudoArgs()+command,cwd=cwd)
    (stdout,stderr) = process.communicate()
    return process.returncode
  
  def callCollectOutput(self,args,cwd=None):
    """
    Run the command and return a tuple with: (returncode,the output to stdout as a string,stderr as a string).
    """
    args = self.getSudoArgs() + args
    process = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=cwd)
    (stdout,stderr) = process.communicate()
    return (process.returncode,stdout.decode("utf-8"),stderr.decode("utf-8"))

  def Popen(self,command,*args,**kwargs):
    return subprocess.Popen(self.getSudoArgs()+command,*args,**kwargs)

  def runEditor(self,filePath):
    """
    Launch a file editor and edit the given filePath.
    """
    try:
      editor = os.environ["EDITOR"]
    except KeyError:
      editor = "/usr/bin/nano"
    def actuallyRunEditor(editor,filePath):
      try:
        self.call([editor,filePath])
      except FileNotFoundError:
        if test.testing:
          return
        editor = input(editor+" not found. Please enter the name of your favorite editor:")
        actuallyRunEditor(editor,filePath)
    actuallyRunEditor(editor,filePath)
