#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import paths
import json
import os
import permissions

def getInstalledPrograms():
 """ Return a dictionary that maps from program name to the last update time.
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
 """ Passing this file a dictionary which maps program names to last update time saves that registry to disk, overwritting the previous one.
 """
 programRegistryPath = paths.getProgramRegistryPath()
 programRegistryFile = open(programRegistryPath,"w")
 json.dump(programRegistry,programRegistryFile)
 programRegistryFile.close()

def registerProgram(programName,programVersion):
 """ Add a program to the registry.  If it is already in the registry, update its last update time. """
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

def hasInstalledDependencies(programName):
 """ Returns true if there are any program's which depend upon this program installed. """
 installedPrograms = getInstalledPrograms()
 for program, timeOfLastUpdate in installedPrograms.iteritems():
  try:
   if permissions.getPermissions(program)["dependency"] == programName:
    return True
  except KeyError:
   pass

def getInstalledDependencies(programName):
 """ Returns returns a list of any installed programs which depend upon this program. """
 installedPrograms = getInstalledPrograms()
 installedDependencies = []
 for program, timeOfLastUpdate in installedPrograms.iteritems():
  try:
   if permissions.getPermissions(program)["dependency"] == programName:
    installedDependencies.append(program)
  except KeyError:
   pass

 return installedDependencies

def getDependencyTree(programName):
 """ Returns a dependency tree list of any available program. """
 dependency = ""
 programDependencyTree = [programName]
 xpermissions = permissions.getPermissions(programName)
 try:
  dependency = xpermissions["dependency"]
 except KeyError:
  return programDependencyTree
 
 while dependency:
  if dependency:
   programDependencyTree.append(dependency)
   xpermissions = permissions.getPermissions(dependency)
   try:
    dependency = xpermissions["dependency"]
   except KeyError:
    return programDependencyTree
    
