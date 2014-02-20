#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import paths
import json
import os
import sys
import collections

def getPermissions(programName):
  """ Return the permissions for the given program. """
  # read permissions.json file
  permissionsFilePath = paths.getPermissionsFilePath(programName)
  if not os.path.exists(permissionsFilePath):
    sys.exit("The permissions.json file for the program "+programName+" does not exist.  All subuser programs must have a permissions.json file as defined by the permissions.json standard: <https://github.com/subuser-security/subuser/blob/master/docs/permissions-dot-json-file-format.md>")
  with open(permissionsFilePath, 'r') as file_f:
    permissions=json.load(file_f, object_pairs_hook=collections.OrderedDict)
    return permissions

def setPermissions(programName,permissions):
  """ Set the permissions of a given program.
  Warning, will mess up the formatting of the json file.
  """
  permissionsFilePath = paths.getPermissionsFilePath(programName)
  with open(permissionsFilePath, 'w') as file_f:
    json.dump(permissions,file_f,indent=1, separators=(',', ': '))

def hasExecutable(programName):
  """ Return True if the program has an executable associated with it. """
  try:
    getPermissions(programName)["executable"]
    return True
  except KeyError:
    return False

# Getters with defaults from subuser/docs/permissions-dot-json-file-format.md

def getExecutable(permissions):
  """ Either returns the path to the program's executable or None if it is a library. """
  return permissions.get("executable",None)

def getSharedHome(permissions):
  """ Either returns the name of the program this program shares it's home dir with or None if it doesn't share it's home dir. """
  return permissions.get("shared-home",None)

def getDependency(permissions):
  """ Either returns the name of the program this program depends on or None if this program has no dependency. """
  return permisssions.get("dependency",None)

def getUserDirs(permissions):
  """ Either returns the user directories this program has access to or an empty list if this program cannot access any user directories. """
  return permissions.get("user-dirs",[])

def getSystemDirs(permissions):
  """ Either returns the system directories this program can read from or an empty list if this program cannot read from any system directories. """
  return permissions.get("system-dirs",[])

def getX11(permissions):
  """ Can this program display X11 windows? """
  return permissions.get("x11",False)

def getSound(permissions):
  """ Can this program access the sound-card? """
  return permissions.get("sound",False)

def getInheritWorkingDirectory(permissions):
  """ Can this program access the directory from which it was launched? """
  return permissions.get("inherit-working-directory",False)

def getAllowNetworkAccess(permissions):
  """ Can this program access the network? """
  return permissions.get("allow-network-access",False)

def getPrivileged(permissions):
  """ Is this program to be run in privileged mode? """
  return permissions.get("privileged",False)
