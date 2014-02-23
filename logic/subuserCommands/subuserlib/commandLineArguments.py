#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import availablePrograms

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
