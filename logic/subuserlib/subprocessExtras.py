#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
Helper functions for running foreign executables.
"""

#external imports
import subprocess
import os
#internal imports
#import ...

def call(args,cwd=None):
  """
  Same as subprocess.call except here you can specify the cwd.

  Returns subprocess's exit code.
  """
  process = subprocess.Popen(args,cwd=cwd)
  (stdout,stderr) = process.communicate()
  return process.returncode

def callBackground(args,cwd=None,suppressOutput=True,collectOutput=False):
  """
  Same as subprocess.call except here you can specify the cwd.
  Returns imediately with the subprocess
  """
  if collectOutput:
    process = subprocess.Popen(args,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  elif suppressOutput:
    devnull = open(os.devnull,"a")
    process = subprocess.Popen(args,cwd=cwd,stdout=devnull,stderr=devnull,close_fds=True)
  else:
    process = subprocess.Popen(args,cwd=cwd)
  return process

def callCollectOutput(args,cwd=None):
  """
  Run the command and return a tuple with: (returncode,the output to stdout as a string).
  """
  process = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=cwd)
  (stdout,stderr) = process.communicate()
  return (process.returncode,stdout.decode("utf-8"))

def runEditor(filePath):
  """
  Launch a file editor and edit the given filePath.
  """
  try:
    editor = os.environ["EDITOR"]
  except KeyError:
    editor = "/usr/bin/nano"
  call([editor,filePath])
