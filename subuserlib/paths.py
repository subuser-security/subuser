# -*- coding: utf-8 -*-

"""
Module used for determining non-user-configurable paths.
"""

#external imports
import os
import inspect
#internal imports
import subuserlib.executablePath as executablePath

home = os.path.expanduser("~")

def upNDirsInPath(path,n):
  if n > 0:
    return os.path.dirname(upNDirsInPath(path,n-1))
  else:
    return path

def getSubuserDir():
  """
  Get the toplevel directory for subuser.
  """
  pathToThisSourceFile = os.path.abspath(inspect.getfile(inspect.currentframe()))
  return upNDirsInPath(pathToThisSourceFile,3)

def getSubuserExecutable():
  executable = os.path.join(getSubuserDir(),"logic","subuser")
  if not os.path.exists(executable):
    executable = executablePath.which("subuser")
  return executable

def getSubuserDataFile(filename):
  dataFile = os.path.join(getSubuserDir(),"logic","subuserlib","data",filename)
  if os.path.exists(dataFile):
    return dataFile
  else:
    import pkg_resources
    dataFile = pkg_resources.resource_filename("subuserlib",os.path.join("data",filename))
    if not os.path.exists(dataFile):
      exit("Data file does not exist:"+str(dataFile))
    else:
      return dataFile
