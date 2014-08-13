#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import os,sys,inspect,json
#internal imports
import permissions,basicPaths

home = basicPaths.home

def getSubuserDir():
  """ Get the toplevel directory for subuser. """
  return basicPaths.getSubuserDir()

def getDockersideScriptsPath():
  return os.path.join(getSubuserDir(),"logic","dockerside-scripts")

def getSubuserCommandsDir():
  """ Return the path to the directory where the individual built-in subuser command executables are stored. """
  return os.path.join(getSubuserDir(),"logic","subuserCommands")

