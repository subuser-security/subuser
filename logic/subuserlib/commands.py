#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
"""
This module helps us figure out which subuser subcommands can be called.
"""

#external imports
import os
#internal imports
import subuserlib.executablePath
import subuserlib.paths

nonCommands = {"__init__.py", "pathConfig.py"}

def getBuiltInSubuserCommands():
  """ Get a list of the names of the built in subuser commands. """
  apparentCommandsSet = set( os.listdir(subuserlib.paths.getSubuserCommandsDir()))
  commands = list(apparentCommandsSet.difference(nonCommands))
  return [command[:-3] for command in commands if not command.endswith(".pyc") and not command.startswith("__")] #remove the .py suffixes.

def getExternalSubuserCommands():
  """ Return the list of "external" subuser commands.  These are not built in commands but rather stand alone executables which appear in the user's $PATH and who's names start with "subuser-" """

  def isPathToSubuserCommand(path):
    directory, executableName = os.path.split(path)
    return executableName.startswith("subuser-")

  externalCommandPaths = subuserlib.executablePath.queryPATH(isPathToSubuserCommand)

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
  builtInCommandPath = os.path.join(subuserlib.paths.getSubuserCommandsDir(),command)
  if os.path.exists(builtInCommandPath):
    return builtInCommandPath
  elif os.path.exists(builtInCommandPath+".py"):
    return (builtInCommandPath+".py")
  else:
    externalCommandPath = subuserlib.executablePath.which("subuser-"+command)
    return externalCommandPath
