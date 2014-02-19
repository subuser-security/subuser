#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import paths
import json
import os
import sys
import permissions

def getInstalledPrograms():
 """ Return a dictionary that maps from program name to the last update time.
 """
 programRegistryPath = paths.getProgramRegistryPath()
 if os.path.exists(programRegistryPath):
  with open(programRegistryPath, 'r') as file_f:
   programRegistry = json.load(file_f)
 else:
  programRegistry = {}
 return programRegistry

def setInstalledPrograms(programRegistry):
 """ Passing this file a dictionary which maps program names to last update time saves that registry to disk, overwritting the previous one.
 """
 programRegistryPath = paths.getProgramRegistryPath()
 with open(programRegistryPath, 'w') as file_f:
  json.dump(programRegistry,file_f)

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
 for program in installedPrograms.keys():
  try:
   if permissions.getPermissions(program)["dependency"] == programName:
    return True
  except KeyError:
   pass

def getInstalledDependencies(programName):
 """ Returns returns a list of any installed programs which depend upon this program. """
 installedPrograms = getInstalledPrograms()
 installedDependencies = []
 for program in installedPrograms.keys():
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

def getDependencyMatrix(subuserProgramList, useHasExecutable=False, sortLists=False):
 """ 
 Returns a dependency matrix dictionary with some extra options 
 
 Arguments: 
 - subuserProgramList: List of available or installed (or a selected list)  of subuser-programs 
      (getInstalledPrograms().keys(), or getAvailablePrograms(), or ["firefox", "vim"]
 - useHasExecutable: boolean: if True a additional key "has-executable" will be added to the matrix
 - sortLists: boolean: if True: required-by, depends-on  will be sorted 
 
 Matrix format: { 'programName' : { 
                     "required-by" : [app1, app2],
                     "depends-on" : [app1, lib3]
                                  }
                }   

 Matrix format: { 'programName' : { 
                     "required-by" : [app1, app2],
                     "depends-on" : [],
                     "has-executable" : True
                                  }
                } 
                
 NOTE: keys are always present: required-by, depends-on can be empty lists too
 """
 dependencyMatrix = {}
 for program in subuserProgramList:
  if useHasExecutable:
   if permissions.getPermissions(program).get("executable", None):
    dependencyMatrix[program] = {"required-by" : [], "depends-on" : [], "has-executable" : True}
   else:
    dependencyMatrix[program] = {"required-by" : [], "depends-on" : [], "has-executable" : False}
  else:
   dependencyMatrix[program] = {"required-by" : [], "depends-on" : []}
   
 #assumption is that the correct list is passed: no point to check here if available: as often the getAvailablePrograms list is used as input
 #using a try instead
 try:
  for programMain in dependencyMatrix.keys():
   for program in getDependencyTree(programMain):
    dependencyMatrix[programMain]["depends-on"].append(program)
    if program != programMain:
     #could be that we got a own list which does not have this included: or a broken installed-programs.json
     if program in dependencyMatrix.keys():
      dependencyMatrix[program]["required-by"].append(programMain)
  
 except Exception as err:
  print("""ERROR:  %s 
   
  Suggestion: maybe it is defined as a wrong dependency in a permission.json file\n""" % (err))
  sys.exit()
   
 #sort if required
 if sortLists:
  for programMain in dependencyMatrix.keys():
   dependencyMatrix[programMain]["depends-on"] = sorted(dependencyMatrix[programMain]["depends-on"])
   dependencyMatrix[programMain]["required-by"] = sorted(dependencyMatrix[programMain]["required-by"])
  
 return dependencyMatrix
