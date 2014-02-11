#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import paths
import json
import os

def getInstalledPrograms():
 """ Return a dictionary that maps from program name to installed version.
 NOTE: the installed versions may not be acurate.  The installed version is the "least possible installed version" the actual version that is installed may be newer!
 """
 programRegistryPath = paths.getProgramRegistryPath()
 if os.path.exists(programRegistryPath):
  programRegistryFile = open(programRegistryPath,"r")
  programRegistry = json.load(programRegistryFile)
  programRegistryFile.close()
 else:
  programRegistry = {}
 return programRegistry

def setInstalledPrograms(programRegistry):
 """ Passing this file a dictionary which maps program names to installed versions saves that registry to disk, overwritting the previous one.
 """
 programRegistryPath = paths.getProgramRegistryPath()
 programRegistryFile = open(programRegistryPath,"w")
 json.dump(programRegistry,programRegistryFile)
 programRegistryFile.close()

def registerProgram(programName,programVersion):
 """ Add a program to the registry.  If it is already in the registry, update its version. """
 programRegistry = getInstalledPrograms()
 programRegistry[programName]=programVersion
 setInstalledPrograms(programRegistry)

def unregisterProgram(programName):
 """ Remove a program from the registry. """
 programRegistry = getInstalledPrograms()
 del programRegistry[programName]
 setInstalledPrograms(programRegistry)

def isProgramInstalled(programName):
 """ Returns true if the program is installed. """
 installedPrograms = getInstalledPrograms()
 try:
  installedPrograms[programName]
  return True
 except KeyError:
  return False
