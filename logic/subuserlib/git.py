#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
"""
Just some helper functions for running git.
"""

#external imports
import sys,os
#internal imports
import subuserlib.subprocessExtras

def runGit(args,cwd=None):
  """ Run git with the given command line arguments. """
  return subuserlib.subprocessExtras.subprocessCheckedCall(["git"]+args,cwd=cwd)

def runGitCollectOutput(args,cwd=None):
  """ Run git with the given command line arguments and return its output. """
  return subuserlib.subprocessExtras.subprocessCheckedCallCollectOutput(["git"]+args,cwd=cwd)

