#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import sys
import subprocess
import availablePrograms

def subprocessCheckedCall(args, addToErrorInfo=''):
  """ simplify subprocess.check_call in other code
  e.g.
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
  """ simplify subprocess.check_output in other code
  returns output or raises error
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
    
def getUserCommandLine(argvList, commandOptionList):
  """ ASSUMPTION: any commandline argument which is not a define option is a program name
  To make it more useful: precheck if all program names are 'really' subuser available programs
  
  returns tuple (preCheckProgramNameList, userOptionList)
  e.g:
  userProgramList = getUserCommandLine(sys.argv[1:], [])[0]
  
  commandOptionList = ['--from-cache']
  userProgramList, userOptionList = getUserCommandLine(sys.argv[1:], commandOptionList)
  """
  preCheckProgramNameList = []
  userOptionList = []
  
  for item in argvList:
    if item in commandOptionList:
      userOptionList.append(item)
    else:
      preCheckProgramNameList.append(item)

  for programName in preCheckProgramNameList:
    if not availablePrograms.available(programName):
      print("<{0}> not an available subuser-program".format(programName))
      print("\nAvailable programs are:")
      print(availablePrograms.getAvailableProgramsText(addNewLine=True, indentSpaces=3))
      sys.exit()
  
  return (preCheckProgramNameList, userOptionList)
