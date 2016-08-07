# -*- coding: utf-8 -*-
"""
This module helps us figure out which subuser subcommands can be called.
"""

#external imports
import os
import subprocess
import sys
import pkgutil
#internal imports
import subuserlib.executablePath
import subuserlib.paths
import subuserlib.builtInCommands

def getBuiltIn():
  """
  Get a list of the names of the built in subuser commands.
  """
  # Ugly hack courtesy of http://stackoverflow.com/questions/487971/is-there-a-standard-way-to-list-names-of-python-modules-in-a-package
  return [name for _, name, _ in pkgutil.iter_modules([os.path.dirname(subuserlib.builtInCommands.__file__)])]

def getExternal():
  """
  Return the list of "external" subuser commands.  These are not built in commands but rather stand alone executables which appear in the user's $PATH and who's names start with "subuser-"
  """
  def isPathToCommand(path):
    directory, executableName = os.path.split(path)
    return executableName.startswith("subuser-")
  externalCommandPaths = subuserlib.executablePath.queryPATH(isPathToCommand,list=True)
  externalCommands = []
  subuserPrefixLength=len("subuser-")
  for externalCommandPath in externalCommandPaths:
    commandDir, executableName = os.path.split(externalCommandPath)
    commandName = executableName[subuserPrefixLength:]
    if commandName.endswith(".py"):
      commandName=commandName[:-3]
    externalCommands.append(commandName)
  return list(set(externalCommands)) # remove duplicate entries

def getCommands():
  """
  Returns a list of commands that may be called by the user.
  """
  return list(set(getBuiltIn() + getExternal()))

def getCommand(command):
  if command in getBuiltIn():
    commandModule = __import__("subuserlib.builtInCommands."+command, fromlist=[''])
    return commandModule.runCommand
  else:
    externalCommandPath = subuserlib.executablePath.which("subuser-"+command)
    if externalCommandPath:
      def runCommand(args):
        sys.exit(subprocess.call([externalCommandPath]+args))
      return runCommand
    else:
      return None
