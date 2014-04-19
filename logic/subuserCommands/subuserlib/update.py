#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

# This command updates all or some of the installed subuser programs.
import sys
import subprocess
import registry
import permissions
import dockerImages
import uninstall
import install
import subprocessExtras
import commandLineArguments
import availablePrograms

#####################################################################################
def getProgramsWhosLastUpdateTimesChanged():
  """ Returns a list of progams who's last-update-time has changed since it was installed. """
  programsWhosLastUpdateTimeChanged = []
  _registry = registry.getRegistry()
  for program, registeredInfo in _registry.iteritems():
    availableLastUpdateTime = permissions.getPermissions(program).get("last-update-time",None)
    installedLastUpdateTime = registeredInfo.get("last-update-time",None)
    if not availableLastUpdateTime == installedLastUpdateTime and not availableLastUpdateTime == None:
      programsWhosLastUpdateTimeChanged.append(program)
  return programsWhosLastUpdateTimeChanged

def uninstall(program):
  uninstall.uninstall(program)

def uninstallProgramsToBeUpdated(programsToBeUpdated):
  programsToBeUninstalled = set(programsToBeUpdated)

  uninstalledPrograms = set([])
  while not programsToBeUninstalled == uninstalledPrograms:
    for program in programsToBeUninstalled:
      if not registry.hasInstalledDependencies(program):
        uninstall(program)
        uninstalledPrograms.add(program)

def installProgramsToBeUpdated(programsToBeUpdated):
  for program in programsToBeUpdated:
    if permissions.hasExecutable(program): # Don't install libraries as these might have changed and no longer be needed.  They'll automatically get installed anyways.
      install.installProgramAndDependencies(program, False)

def runUpdate(programsToBeUpdated):
  print("The following programs will be updated:")
  for program in programsToBeUpdated:
    print(program)
  choice = raw_input("Do you want to continue updating [y/n]? " )
  if choice in ["Y","y"]:
    uninstallProgramsToBeUpdated(programsToBeUpdated)
    installProgramsToBeUpdated(programsToBeUpdated)
  else:
    sys.exit()

  while dockerImages.areProgramsRunning(programsToBeUpdated):
    print("PLEASE: close these programs before continuing. If there seem to be containers hanging around when the program isn't even running you might try:")
    print(" $ docker kill <container-id>")
    print("You still need to close:")
    for runningProgram in dockerImages.getRunningProgramsWithNames(programsToBeUpdated):
      print(runningProgram)
    shouldQuit = raw_input("Press enter to continue(or q to quit): ")
    if shouldQuit == 'q':
      exit()

def updateSomePrograms(programs):
  programsToBeUpdated = set()
  dependencyMatrix = registry.getDependencyMatrix(availablePrograms.getAvailablePrograms())
  for program in programs:
    programsToBeUpdated.add(program)
    for dependent in dependencyMatrix[program]["required-by"]:
      if registry.isProgramInstalled(dependent):
        programsToBeUpdated.add(dependent)
  runUpdate(list(programsToBeUpdated))

def needsUpdate(program):
  """ Returns true if the program or any of it's dependencies need to be updated. """
  _registry = registry.getRegistry()
  dependencyMatrix = registry.getDependencyMatrix(availablePrograms.getAvailablePrograms())
  programsToCheck = dependencyMatrix[program]["depends-on"]
  programsToCheck.append(program)
  for programToCheck in programsToCheck:
    myPermissions = permissions.getPermissions(programToCheck)
    if not permissions.getLastUpdateTime(myPermissions) == _registry[programToCheck]["last-update-time"] and not permissions.getLastUpdateTime(myPermissions) == None:
      return True
  return False
