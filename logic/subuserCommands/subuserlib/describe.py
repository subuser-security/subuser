#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import subuserlib.permissions
import subuserlib.availablePrograms
import subuserlib.registry
import subuserlib.dockerImages

def printInfo(program,showProgramStatus):
 """ Print information about a given program to standard output. """
 registry = subuserlib.registry.getRegistry()

 if not subuserlib.availablePrograms.available(program):
  print(program + " does not exist.\n")
 else:
  permissions = subuserlib.permissions.getPermissions(program)
  print(program+":")
  print(" Description: "+permissions["description"])
  print(" Maintainer: "+permissions["maintainer"])
  if showProgramStatus:
   print(" Running: "+str(subuserlib.dockerImages.isProgramRunning(program)))
   if "last-update-time" in permissions.keys():
    print(" Needs update: "+str(not permissions["last-update-time"] == registry[program]["last-update-time"]))
  if subuserlib.permissions.getExecutable(permissions):
   print(" Executable: "+subuserlib.permissions.getExecutable(permissions))
  else:
   print(" Is a library")
  if subuserlib.permissions.getSharedHome(permissions):
   print(" Shares it's home directory with: "+subuserlib.permissions.getSharedHome(permissions))
  # TODO print dependencies.
  # TODO actually prety print the user-dirs and system-dirs lists.
  if not subuserlib.permissions.getUserDirs(permissions)==[]:
   print(" Has access to the following user directories: "+str(subuserlib.permissions.getUserDirs(permissions)))
  if not subuserlib.permissions.getSystemDirs(permissions)==[]:
   print(" Can read from the following system directories: "+str(subuserlib.permissions.getSystemDirs(permissions)))
  if subuserlib.permissions.getX11(permissions):
   print(" Can display X11 windows.")
  if subuserlib.permissions.getSound(permissions):
   print(" Has access to your soundcard, can play sounds/record sound.")
  if subuserlib.permissions.getInheritWorkingDirectory(permissions):
   print(" Can access the directory from which it was launched.")
  if subuserlib.permissions.getAllowNetworkAccess(permissions):
   print(" Can access the network/internet.")
  if subuserlib.permissions.getPrivileged(permissions):
   print(" Is fully privileged.  NOTE: Highly insecure!")
