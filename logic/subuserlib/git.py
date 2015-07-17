#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
"""
Just some helper functions for running git.
"""

#external imports
#import ...
#internal imports
import subuserlib.subprocessExtras,tempfile

def runGit(args,cwd=None):
  """ Run git with the given command line arguments. """
  return subuserlib.subprocessExtras.subprocessCheckedCall(["git"]+args,cwd=cwd)

def commit(message,cwd=None):
  """ Run git commit with the given commit message. """
  try:
    tempFile = tempfile.NamedTemporaryFile("w",encoding="utf-8")
  except TypeError: # Older versions of python have broken tempfile implementation for which you cannot set the encoding.
    tempFile = tempfile.NamedTemporaryFile("w")
    message = message.encode('ascii', 'ignore').decode('ascii')

  with tempFile as tempFile:
    tempFile.write(message)
    tempFile.flush()
    return subuserlib.subprocessExtras.subprocessCheckedCall(["git","commit","--file",tempFile.name],cwd=cwd)

def runGitCollectOutput(args,cwd=None):
  """ Run git with the given command line arguments and return its output. """
  return subuserlib.subprocessExtras.subprocessCheckedCallCollectOutput(["git"]+args,cwd=cwd)

