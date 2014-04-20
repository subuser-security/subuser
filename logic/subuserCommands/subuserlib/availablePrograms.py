#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import os
#internal imports
import paths

def available(programName):
  """ Returns True if the program is available for instalation. """
  return not paths.getProgramSrcDir(programName) == None

def getAvailablePrograms():
  """ Returns a list of program's available for instalation. """
  repoPaths = paths.getRepoPaths()
  availablePrograms = []
  for path in repoPaths:
    availablePrograms += os.listdir(path)
  return availablePrograms
