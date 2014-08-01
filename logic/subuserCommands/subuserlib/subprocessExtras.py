#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import sys,subprocess
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
  """ This helper function calls subprocess.check_call and runs sys.exit rather than throwing an error when the program exits with a non-zero exit code.

 Usage:
  subprocessCheckedCall(["docker", "-d"], "ATTENTION: Special added info bla bla")
  """
  process = subprocess.Popen(args,cwd=cwd)
  process.communicate()
  err = ""
  if not process.returncode == 0:
    sys.exit(formatErrorMessage(args,err,errorContext=errorContext))
    
def subprocessCheckedOutput(args, errorContext=''):
  """ This function calls subprocess.check_output and uses sys.exit when the call fails rather than throwing an error.

 Usage:
  subprocessCheckedOutput(["docker", "-d"], "ATTENTION: Special added info bla bla")
  """
  try:
    return subprocess.check_output(args)
  except Exception as err:
    formatErrorMessage(args,err,errorContext=errorContext)
    sys.exit(message)
