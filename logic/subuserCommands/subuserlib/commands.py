#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import os
#internal imports
import executablePath,paths

nonCommands = {"__init__.py", "__init__.pyc", "subuserlib"}

def getBuiltInSubuserCommands():
  """ Get a list of the names of the built in subuser commands. """
  apparentCommandsSet = set( os.listdir(paths.getSubuserCommandsDir()))
  return list(apparentCommandsSet.difference(nonCommands))

def getExternalSubuserCommands():
  """ Return the list of "external" subuser commands.  These are not built in commands but rather stand alone executables which appear in the user's $PATH and who's names start with "subuser-" """

  def isPathToSubuserCommand(path):
    directory, executableName = os.path.split(path)
    return executableName[:8] == "subuser-"

  externalCommandPaths = executablePath.queryPath(isPathToSubuserCommand)
  externalCommands = []

  for externalCommandPath in externalCommandPaths: 
    commandDir, executableName = os.path.split(externalCommandPath)
    commandName = executableName[8:]
    externalCommands.append(commandName)

  return externalCommands

def getSubuserCommands():
  """ Returns a list of commands that may be called by the user. """
  return getBuiltInSubuserCommands() + getExternalSubuserCommands()

def getSubuserCommandPath(command):
  builtInCommandPath = os.path.join(_getSubuserCommandsPath(),command)
  if os.path.exists(builtInCommandPath):
    return builtInCommandPath
  else:
    externalCommandPath = executablePath.which("subuser-"+command)
    return externalCommandPath
