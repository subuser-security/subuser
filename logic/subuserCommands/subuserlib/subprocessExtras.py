#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import sys
import subprocess

def subprocessCheckedCall(args, addToErrorInfo=''):
  """ This helper function calls subprocess.check_call and runs sys.exit rather than throwing an error when the program exits with a non-zero exit code.

 Usage:
  subprocessCheckedCall(["docker", "-d"], "ATTENTION: Special added info bla bla")
  """
  try:
    subprocess.check_call(args)
  except Exception as err:
    if addToErrorInfo:
      message = ('''Command <{0}> failed:\n  ERROR: {1}\n    {2}'''.format(' '.join(args), err, addToErrorInfo))
    else:
      message = ('''Command <{0}> failed:\n  ERROR: {1}'''.format(' '.join(args), err))
    sys.exit(message)
    
def subprocessCheckedOutput(args, addToErrorInfo=''):
  """ This function calls subprocess.check_output and uses sys.exit when the call fails rather than throwing an error.

 Usage:
  subprocessCheckedOutput(["docker", "-d"], "ATTENTION: Special added info bla bla")
  """
  try:
    return subprocess.check_output(args)
  except Exception as err:
    if addToErrorInfo:
      message = ('''Command <{0}> failed:\n  ERROR: {1}\n    {2}'''.format(' '.join(args), err, addToErrorInfo))
    else:
      message = ('''Command <{0}> failed:\n  ERROR: {1}'''.format(' '.join(args), err))
    sys.exit(message)
