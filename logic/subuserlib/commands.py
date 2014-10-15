#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import os
#internal imports
import executablePath,paths

nonCommands = {"__init__.py", "__init__.pyc", "pathConfig.py"}

def getBuiltInSubuserCommands():
  """ Get a list of the names of the built in subuser commands. """
  apparentCommandsSet = set( os.listdir(paths.getSubuserCommandsDir()))
  commands = list(apparentCommandsSet.difference(nonCommands))
  return [command[:-3] for command in commands] #remove the .py suffixes.

def getExternalSubuserCommands():
  """ Return the list of "external" subuser commands.  These are not built in commands but rather stand alone executables which appear in the user's $PATH and who's names start with "subuser-" """

  def isPathToSubuserCommand(path):
    directory, executableName = os.path.split(path)
    return executableName.startswith("subuser-")

  externalCommandPaths = executablePath.queryPATH(isPathToSubuserCommand)

  externalCommands = []
  subuserPrefixLength=len("subuser-")
  for externalCommandPath in externalCommandPaths: 
    commandDir, executableName = os.path.split(externalCommandPath)
    commandName = executableName[subuserPrefixLength:]
    externalCommands.append(commandName)
  
  return list(set(externalCommands)) # remove duplicate entries

def getSubuserCommands():
  """ Returns a list of commands that may be called by the user. """
  return getBuiltInSubuserCommands() + getExternalSubuserCommands()

def getSubuserCommandPath(command):
  builtInCommandPath = os.path.join(paths.getSubuserCommandsDir(),command)
  if os.path.exists(builtInCommandPath):
    return builtInCommandPath
  elif os.path.exists(builtInCommandPath+".py"):

    return (builtInCommandPath+".py")
  else:
    externalCommandPath = executablePath.which("subuser-"+command)
    return externalCommandPath
