#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import sys
import subprocess
import availablePrograms

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
    
def parseCommandLineArgs(argvList, commandOptionList):
  """
This function parses a list of command line arguments.

It returns a tuple (preCheckProgramNameList, userOptionList) where preCheckProgramNameList is a list of names of programs and userOptionList is a list of options that have been passed.  Simply put, anything that that you pass in the seccond argument to this function is an option, everything else is added to the preCheckProgramNameList.
 
 e.g:
  userProgramList = parseCommandLineArgs(sys.argv[1:], [])[0]
  
  commandOptionList = ['--from-cache']
  userProgramList, userOptionList = parseCommandLineArgs(sys.argv[1:], commandOptionList)
  """
  preCheckProgramNameList = []
  userOptionList = []
  
  for item in argvList:
    if item in commandOptionList:
      userOptionList.append(item)
    else:
      preCheckProgramNameList.append(item)

  return (preCheckProgramNameList, userOptionList)
