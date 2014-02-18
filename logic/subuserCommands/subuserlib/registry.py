#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import sys
import paths
import json
import os
import subprocess
import permissions
import availablePrograms

def getInstalledPrograms():
 """ Return a dictionary that maps from program name to registered items
 registered items:
  - LastUpdateTime
  - ImageID
 """
 programRegistry = {}
 programRegistryPath = paths.getProgramRegistryPath()
 if os.path.exists(programRegistryPath):
  with open(programRegistryPath, 'r') as file_f:
   programRegistry = json.load(file_f)
   
 #Maintaining backwards compat: to be soon removed
 if len(programRegistry) > 0:
  firstProgramName = programRegistry.keys()[0]
  if not isinstance(programRegistry[firstProgramName], dict):
   programNewRegistry = {}
   for programName, lastUpdateTime in programRegistry.iteritems():
    programNewRegistry[programName] = {}
    programNewRegistry[programName]['LastUpdateTime'] = lastUpdateTime
    #Try to get the ImageID
    dockerCommand = """(sudo docker inspect subuser-%s | grep id | cut -d '"' -f 4)""" %  programName
    try:
     programImageID = subprocess.check_output([dockerCommand], shell=True)
     programNewRegistry[programName]['ImageID'] = programImageID.strip()
     programRegistry = programNewRegistry
     #save the new one here once and for all
     setInstalledPrograms(programRegistry)
    except Exception as err:
     print("ERROR: getting programDockerImageID: %s" % err)
     sys.exit("""\nYou still use the old <installed-programs.json> format.
   
You could delete the <installed-programs.json>  and try to reinstall all programs with the:  --from-cache option""")
 return programRegistry

def setInstalledPrograms(programRegistry):
 """ Passing this file a dictionary which maps program names to registered items writes that registry to disk, overwritting the previous one.
 registered items:
  - LastUpdateTime
  - ImageID
 """
 programRegistryPath = paths.getProgramRegistryPath()
 with open(programRegistryPath, 'w') as file_f:
  json.dump(programRegistry, file_f, indent=1, separators=(',', ': '))

def registerProgram(programName, programLastUpdateTime, programImageID):
 """ Add a program to the registry.  If it is already in the registry, update its registered items. 
 registered items:
  - LastUpdateTime
  - ImageID
 """
 programRegistry = getInstalledPrograms()
 programRegistry[programName] = {}
 programRegistry[programName]['LastUpdateTime'] = programLastUpdateTime
 programRegistry[programName]['ImageID'] = programImageID
 setInstalledPrograms(programRegistry)

def unregisterProgram(programName):
 """ Remove a program from the registry. """
 programRegistry = getInstalledPrograms()
 if programName in programRegistry.keys():
  del programRegistry[programName]
  setInstalledPrograms(programRegistry)

def isProgramInstalled(programName):
 """ Returns true if the program is installed. """
 programRegistry = getInstalledPrograms()
 if programName in programRegistry.keys():
  return True
 else:
  return False

def hasInstalledDependencies(programName):
 """ Returns true if there are any program's which depend upon this program installed. """
 programRegistry = getInstalledPrograms()
 for program in programRegistry.keys():
  try:
   if permissions.getPermissions(program)["dependency"] == programName:
    return True
  except KeyError:
   pass

def getInstalledDependencies(programName):
 """ Returns returns a list of any installed programs which depend upon this program. """
 programRegistry = getInstalledPrograms()
 installedDependencies = []
 for program in programRegistry.keys():
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
 programPermissions = permissions.getPermissions(programName)
 dependency = programPermissions.get("dependency", None)
 if dependency:
  while dependency:
   if dependency:
    programDependencyTree.append(dependency)
    programPermissions = permissions.getPermissions(dependency)
    dependency = programPermissions.get("dependency", None)
    if not dependency:
     break 
 return programDependencyTree
