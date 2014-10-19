#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
Module used for determining non-user-configurable paths.
"""

#external imports
import os
#internal imports
import subuserlib.basicPaths

home = subuserlib.basicPaths.home

def getSubuserDir():
  """ Get the toplevel directory for subuser. """
  return subuserlib.basicPaths.getSubuserDir()

def getDockersideScriptsPath():
  return os.path.join(getSubuserDir(),"logic","dockerside-scripts")

def getSubuserCommandsDir():
  """ Return the path to the directory where the individual built-in subuser command executables are stored. """
  return os.path.join(getSubuserDir(),"logic","subuserCommands")

