#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import paths
import json
import os
import sys
import permissions
import subuserlib.availablePrograms

def getRegistry():
 """ Return a dictionary of the program registry: installed-programs.json
 """
 programRegistryPath = paths.getProgramRegistryPath()
 if os.path.exists(programRegistryPath):
  with open(programRegistryPath, 'r') as file_f:
   programRegistry = json.load(file_f)
 else:
  programRegistry = {}
 return programRegistry
 
def getInstalledPrograms():
 """ Returns a list of installed programs. 
 """
 return getRegistry().keys()

def setInstalledPrograms(programRegistry):
 """ Passing this file a dictionary which maps program names to last update time saves that registry to disk, overwritting the previous one.
 """
 programRegistryPath = paths.getProgramRegistryPath()
 with open(programRegistryPath, 'w') as file_f:
  json.dump(programRegistry,file_f)

def registerProgram(programName,programVersion):
 """ Add a program to the registry.  If it is already in the registry, update its last update time. """
 programRegistry = getRegistry()
 programRegistry[programName]=programVersion
 setInstalledPrograms(programRegistry)

def unregisterProgram(programName):
 """ Remove a program from the registry. """
 programRegistry = getRegistry()
 del programRegistry[programName]
 setInstalledPrograms(programRegistry)

def isProgramInstalled(programName):
 """ Returns true if the program is installed. """
 installedPrograms = getRegistry()
 try:
  installedPrograms[programName]
  return True
 except KeyError:
  return False

def hasInstalledDependencies(programName):
 """ Returns true if there are any program's which depend upon this program installed. """
 for program in getInstalledPrograms():
  try:
   if permissions.getPermissions(program)["dependency"] == programName:
    return True
  except KeyError:
   pass

def getInstalledDependencies(programName):
 """ Returns returns a list of any installed programs which depend upon this program. """
 installedDependencies = []
 for program in getInstalledPrograms():
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
 while dependency:
  if not subuserlib.availablePrograms.available(dependency):
   sys.exit(programName+" depends upon "+dependency+" however "+dependency+" does not exist.")
  programDependencyTree.append(dependency)
  programPermissions = permissions.getPermissions(dependency)
  dependency = programPermissions.get("dependency", None)
 return programDependencyTree

def getDependencyMatrix(programList, useHasExecutable=False, sortLists=False):
 """ 
 Returns a programName<->dependency info dictionary.
 
 Arguments: 
 - programList: List of available or installed (or a selected list)  of subuser-programs 
      (getInstalledPrograms(), or getAvailablePrograms(), or ["firefox", "vim"]
 - useHasExecutable: boolean: if True an additional key "has-executable" will be added to the matrix
 - sortLists: boolean: if True: required-by, depends-on  will be sorted 
 
 Matrix format when useHasExecutable is False:
                { 'programName' : { 
                     "required-by" : [app1, app2],
                     "depends-on" : [app1, lib3]
                                  }
                }   

 Matrix format when useHasExecutable is True
                { 'programName' : { 
                     "required-by" : [app1, app2],
                     "depends-on" : [],
                     "has-executable" : True
                                  }
                } 
                
 NOTE: The following keys are always present: required-by, depends-on though they may be empty lists
 """

 # Create a dictionary of empty matrices.
 dependencyMatrix = {}
 for program in programList:
  if useHasExecutable:
   if permissions.hasExecutable(program):
    dependencyMatrix[program] = {"required-by" : [], "depends-on" : [], "has-executable" : True}
   else:
    dependencyMatrix[program] = {"required-by" : [], "depends-on" : [], "has-executable" : False}
  else:
   dependencyMatrix[program] = {"required-by" : [], "depends-on" : []}
   
 for program in dependencyMatrix.keys():
  for dependency in getDependencyTree(program):
   if dependency != program:
    dependencyMatrix[program]["depends-on"].append(dependency)
    #could be that we got a own list which does not have this included: or a broken installed-programs.json
    if dependency in dependencyMatrix.keys():
     dependencyMatrix[dependency]["required-by"].append(program)

 #sort if required
 if sortLists:
  for program in dependencyMatrix.keys():
   dependencyMatrix[program]["depends-on"] = sorted(dependencyMatrix[program]["depends-on"])
   dependencyMatrix[program]["required-by"] = sorted(dependencyMatrix[program]["required-by"])
 
 return dependencyMatrix
