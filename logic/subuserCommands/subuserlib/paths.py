#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import os
import inspect

home = os.path.expanduser("~")

def getSubuserDir():
 """ Get the toplevel directory for subuser. """
 return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))) # BLEGH!

def getProgramSrcDir(progName):
 """
 Get the directory where the "source" of the application is stored.  That is the permissions list and the docker-image directory.
 """
 programSourceDir = os.path.join(getSubuserDir(),"programsThatCanBeInstalled",progName)
 return programSourceDir

def getExecutablePath(progName):
 """
 Get the path to the executable that we will be installing.
 """
 executablePath = os.path.join(getSubuserDir(),"bin",progName)
 return executablePath

def getPermissionsFilePath(programName):
 """ Return the path to the given programs permissions file. """
 sourceDir = getProgramSrcDir(programName)
 return os.path.join(sourceDir,"permissions.json")

def getProgramRegistryPath():
 """ Return the path to the list of installed programs json file. """
 return os.path.join(getSubuserDir(),"installed-programs.json")

def getAvailableProgramsPath():
 """ Return the path to the directory which contains sources of programs available for instalation. """
 return os.path.join(getSubuserDir(),"programsThatCanBeInstalled")

def getProgramHomeDirOnHost(programName):
 """ Each program has it's own home directory(or perhaps a shared one).
     This directory has two absolute paths:
      The path to the directory as it appears on the host machine,
      and the path to the directory in the docker container.
     Return the path to the directory as it appears on the host macine. """
 import permissions
 permissions = permissions.getPermissions(programName)
 try:
  sharedHome = permissions["shared-home"]
  return os.path.join(getSubuserDir(),"homes",sharedHome)
 except KeyError:
  return os.path.join(getSubuserDir(),"homes",programName)

def getSubuserCommandsPath():
 """ Return the path to the directory where the individual subuser command executables are stored. """
 return os.path.join(getSubuserDir(),"logic","subuserCommands")

def getSubuserCommandPath(command):
 return os.path.join(getSubuserCommandsPath(),command)

def getDockersideScriptsPath():
 return os.path.join(getSubuserDir(),"logic","dockerside-scripts")
 
def getAvailableProgramsSavedCompressedImagePath():
 """ Return the path to the directory which contains saved compressed docker images of programs available for instalation. """
 return os.path.join(getSubuserDir(),"savedCompressedProgramImages")
