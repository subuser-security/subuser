#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
This is a Class which allows one to manipulate a git repository.
"""

#external imports
import os
import tempfile
#internal imports
import subuserlib.subprocessExtras as subprocessExtras

class GitRepository():
  def __init__(self,path):
    self.__path = path

  def getPath(self):
    return self.__path
  
  def run(self,args):
    """
    Run git with the given command line arguments.
    """
    return subprocessExtras.call(["git"]+args,cwd=self.getPath())
  
  def runCollectOutput(self,args):
    """
    Run git with the given command line arguments and return a tuple with (returncode,output).
    """
    return subprocessExtras.callCollectOutput(["git"]+args,cwd=self.getPath())
 
  def ls(self,commitHash, subfolder,extraArgs=[]):
    """
    Returns a list of file and folder paths.
    Paths are relative to the repository as a whole.
    """
    if not subfolder.endswith("/"):
      subfolder += "/"
    if subfolder == "/":
      subfolder = "./"
    (returncode,output) = self.runCollectOutput(["ls-tree","--name-only"]+extraArgs+[commitHash,subfolder])
    if returncode != 0:
      raise OSError("Git ls-tree failed:"+output)
    return output.splitlines()

  def lsFiles(self,commitHash,subfolder):
    """
    Returns a list of paths to files in the subfolder.
    Paths are relative to the repository as a whole.
    """
    return list(set(self.ls(commitHash,subfolder)) - set(self.lsFolders(commitHash,subfolder)))

  def lsFolders(self,commitHash,subfolder):
    """
    Returns a list of paths to folders in the subfolder.
    Paths are relative to the repository as a whole.
    """
    return self.ls(commitHash,subfolder,["-d"])

  def show(self,commitHash,path):
    """
    Returns the contents of the given file at the given commit.
    """
    (errorcode,content) = self.runCollectOutput(["show",commitHash+":"+path])
    return content

  def commit(self,message):
    """
    Run git commit with the given commit message.
    """
    try:
      tempFile = tempfile.NamedTemporaryFile("w",encoding="utf-8")
    except TypeError: # Older versions of python have broken tempfile implementation for which you cannot set the encoding.
      tempFile = tempfile.NamedTemporaryFile("w")
      message = message.encode('ascii', 'ignore').decode('ascii')
    with tempFile as tempFile:
      tempFile.write(message)
      tempFile.flush()
      return self.run(["commit","--file",tempFile.name])

  def checkout(self,hash,files=[]):
    """
    Run git checkout
    """
    self.run(["checkout",hash]+files)
