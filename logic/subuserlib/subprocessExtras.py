#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
Helper functions for running foreign executables.
"""

#external imports
import sys,subprocess,os
#internal imports
#import ...

def formatErrorMessage(command,error,errorContext=None):
  """
  Takes a command(a list of strings), an error, and an error context, and returns a nicely formatted error message.
  """
  if errorContext:
    return "Command <"+' '.join(command)+"> failed:\n  ERROR: "+errorContext+"\n"+error
  else:
    return "Command <"+' '.join(command)+"> failed. \nERROR: "+error

def subprocessCheckedCall(args, errorContext='',cwd=None):
  """ This helper function calls subprocess.check_call and runs sys.exit rather than throwing an error when the image exits with a non-zero exit code.

 Usage:
  subprocessCheckedCall(["docker", "-d"], "ATTENTION: Special added info bla bla")
  """
  if not cwd:
    cwd = os.getcwd()
  process = subprocess.Popen(args,cwd=cwd)
  process.communicate()
  if not process.returncode == 0:
    sys.exit(formatErrorMessage(args,"running command in dir: "+cwd,errorContext=errorContext))

def subprocessCallPlus(args,cwd=None):
  """
  Same as subprocess.call except here you can specify the cwd.
  """
  process = subprocess.Popen(args,cwd=cwd)
  (stdout,stderr) = process.communicate()
  return process.returncode

def subprocessCallBackground(args,cwd=None):
  """
  Same as subprocess.call except here you can specify the cwd.
  Returns imediately with the subprocesses pid.
  """
  devnull = open(os.devnull,"a")
  process = subprocess.Popen(args,cwd=cwd,stdout=devnull,stderr=devnull,close_fds=True)
  return process.pid



def subprocessCheckedCallCollectOutput(args,errorContext="",cwd=None):
  """
  Run the command and return the output to stdout as a string.
  """
  process = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=cwd)
  (stdout,stderr) = process.communicate()
  if not process.returncode == 0:
    if cwd:
      errorContext = "In directory: "+cwd+"\n"+errorContext
    sys.exit(formatErrorMessage(args,stderr,errorContext=errorContext))
  return stdout.decode("utf-8")

def subprocessCheckedOutput(args, errorContext=''):
  """ This function calls subprocess.check_output and uses sys.exit when the call fails rather than throwing an error.

 Usage:
  subprocessCheckedOutput(["docker", "-d"], "ATTENTION: Special added info bla bla")
  """
  try:
    return subprocess.check_output(args)
  except Exception as err:
    sys.exit(formatErrorMessage(args,err,errorContext=errorContext))
