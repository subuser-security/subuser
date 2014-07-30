#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import sys,os,subprocess
#internal imports
import subprocessExtras,executablePath

def runGit(args,cwd=None):
  """ Run git with the given command line arguments. """
  return subprocess.POpen(["git"]+args,cwd=cwd).communicate()
