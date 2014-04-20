#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import time
#internal imports
import permissions,availablePrograms,paths

installTimeFormat = "%Y-%m-%d-%H:%M"

def currentTimeString():
  """ Return the current time formatted as per spec. """
  return time.strftime(installTimeFormat ,time.gmtime(time.time()))

def markProgramAsNeedingUpdate(programName):
  if not availablePrograms.available(programName):
    print(programName+ " is not the name of any known program.  Cannot mark it as having an update.")
    print("\nAvailable programs are: ")
    availableProgramsPath = paths.getAvailableProgramsPath()
    print(' '.join(sorted([program for program in os.listdir(availableProgramsPath)])))
  else:
    permissions_ = permissions.getPermissions(programName)
    permissions_["last-update-time"] = currentTimeString()
    permissions.setPermissions(programName,permissions_)
