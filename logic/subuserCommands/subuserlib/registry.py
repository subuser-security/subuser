#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
This module provides tools for reading and writting the installed-programs.json file which holds a registry of all installed subuser programs.

To read more about the installed-programs.json file format see docs/installed-programs-dot-json-file-format.md

"""

#external imports
import json,os,sys
#internal imports
import paths,permissions,availablePrograms,dockerImages

def getRegistry():
  """ Return a dictionary of the program registry: installed-programs.json

See docs/installed-programs-dot-json-file-format.md for the registered attributes.

  """
  programRegistry = {}
  programRegistryPath = paths.getProgramRegistryPath()
  if os.path.exists(programRegistryPath):
    with open(programRegistryPath, 'r') as file_f:
      programRegistry = json.load(file_f)

  #Maintain backwards compatability.  TODO, remove this code after a reasonable interval.
  updateNeeded = False
  for program in programRegistry.keys():
    if not "source-repo" in programRegistry[program]:
      programRegistry[program]["source-repo"] = "default"
      updateNeeded = True
    if not "source-name" in programRegistry[program]:
      programRegistry[program]["source-name"] = program
      updateNeeded = True
  if updateNeeded: #save the new one here once and for all
    setInstalledPrograms(programRegistry)
  return programRegistry

def getInstalledPrograms():
  """ Returns a list of installed programs.
  """
  return getRegistry().keys()

def setInstalledPrograms(programRegistry):
  """ Passing this file a dictionary which maps program names to registered items writes that registry to disk, overwritting the previous one.

See docs/installed-programs-dot-json-file-format.md for the registered attributes.
    """
  programRegistryPath = paths.getProgramRegistryPath()
  with open(programRegistryPath, 'w') as file_f:
    json.dump(programRegistry, file_f, indent=1, separators=(',', ': '))

def registerProgram(programName, lastUpdateTime, imageID,sourceRepo, sourceName):
  """ Add a program to the registry.  If it is already in the registry, update its registered items.

See docs/installed-programs-dot-json-file-format.md for the registered attributes.
    """
  programRegistry = getRegistry()
  programRegistry[programName] = {}
  programRegistry[programName]['last-update-time'] = lastUpdateTime
  programRegistry[programName]['image-id'] = imageID
  programRegistry[programName]['source-repo'] = sourceRepo
  programRegistry[programName]['source-name'] = sourceName
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

def getInstalledDependents(programName):
  """ Returns returns a list of any installed programs which depend upon this program. """
  installedDependents = []
  for program in getInstalledPrograms():
    try:
      if permissions.getPermissions(program)["dependency"] == programName:
        installedDependents.append(program)
    except KeyError:
      pass

  return installedDependents

def getDependencyTree(programName):
  """ Returns a dependency tree list of any available program. """
  dependency = ""
  programDependencyTree = [programName]
  programPermissions = permissions.getPermissions(programName)
  dependency = programPermissions.get("dependency", None)
  while dependency:
    if not availablePrograms.available(dependency):
      sys.exit(programName+" depends upon "+dependency+" however "+dependency+" does not exist.")
    programDependencyTree.append(dependency)
    programPermissions = permissions.getPermissions(dependency)
    dependency = programPermissions.get("dependency", None)
  return programDependencyTree

def _createEmptyDependencyTable(programList,useHasExecutable):
  dependencyTable = {}
  for program in programList:
    if useHasExecutable:
      if permissions.hasExecutable(program):
        dependencyTable[program] = {"required-by" : [], "depends-on" : [], "has-executable" : True}
      else:
        dependencyTable[program] = {"required-by" : [], "depends-on" : [], "has-executable" : False}
    else:
      dependencyTable[program] = {"required-by" : [], "depends-on" : []}
  return dependencyTable


def _sortFieldsInDependencyTable(dependencyTable):
  for program in dependencyTable.keys():
    dependencyTable[program]["depends-on"] = sorted(dependencyTable[program]["depends-on"])
    dependencyTable[program]["required-by"] = sorted(dependencyTable[program]["required-by"])


def getDependencyTable(programList, useHasExecutable=False, sortLists=False):
  """
  Returns a programName<->dependency info dictionary.

  Arguments:
  - programList: List of available or installed (or a selected list)  of subuser-programs
            (getInstalledPrograms(), or getAvailablePrograms(), or ["firefox", "vim"]
  - useHasExecutable: boolean: if True an additional key "has-executable" will be added to the table
  - sortLists: boolean: if True: required-by, depends-on  will be sorted

  Table format when useHasExecutable is False:
                                { 'programName' : {
                                          "required-by" : [app1, app2],
                                          "depends-on" : [app1, lib3]
                                                                    }
                                }

  Table format when useHasExecutable is True
                                { 'programName' : {
                                          "required-by" : [app1, app2],
                                          "depends-on" : [],
                                          "has-executable" : True
                                                                    }
                                }

  NOTE: The following keys are always present: required-by, depends-on though they may be empty lists
  """

  # Create a dictionary of empty matrices.
  dependencyTable = _createEmptyDependencyTable(programList,useHasExecutable)

  def markAsRequiredBy(program):
    """ Add this program to the "required-by" field of any program that depends upon it. """
    if dependency in dependencyTable.keys():
      dependencyTable[dependency]["required-by"].append(program)

  for program in dependencyTable.keys():
    for dependency in getDependencyTree(program):
      if dependency != program:
        dependencyTable[program]["depends-on"].append(dependency)
        markAsRequiredBy(program)
  #sort if required
  if sortLists:
    _sortFieldsInDependencyTable(dependencyTable)
  return dependencyTable
