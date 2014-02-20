#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import paths
import os

def available(programName):
  """ Returns True if the program is available for instalation. """
  return os.path.exists(paths.getProgramSrcDir(programName))

def getAvailablePrograms():
  """ Returns a list of program's available for instalation. """
  availableProgramsPath = paths.getAvailableProgramsPath()
  return os.listdir(availableProgramsPath)
