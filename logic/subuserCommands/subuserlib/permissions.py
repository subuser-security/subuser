#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import json,os,sys,collections
#internal imports
import paths

allProgramsMustHavePermissions = "All subuser programs must have a permissions.json file as defined by the permissions.json standard: <https://github.com/subuser-security/subuser/blob/master/docs/permissions-dot-json-file-format.md>"

def getPermissions(programName):
  """ Return the permissions for the given program. """
  # read permissions.json file
  permissionsFilePath = paths.getPermissionsFilePath(programName)
  if permissionsFilePath == None:
    sys.exit("The permissions.json file for the program "+programName+" does not exist.  "+allProgramsMustHavePermissions)
  with open(permissionsFilePath, 'r') as file_f:
    try:
      permissions=json.load(file_f, object_pairs_hook=collections.OrderedDict)
    except ValueError:
      sys.exit("The permissions.json file for the program "+programName+" is not valid json.  "+allProgramsMustHavePermissions)
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

def getLastUpdateTime(permissions):
  """ Returns the last-update-time of the program in the repo.  This basically works like a version number but is less semantic. """
  return permissions.get("last-update-time",None)

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

def getGraphicsCard(permissions):
  """ Is this program allowed to access the GPU directly(AKA, do OpenGL stuff). """
  return permissions.get("graphics-card",False)

def getSoundCard(permissions):
  """ Can this program access the sound-card? """
  sound = permissions.get("sound-card",False)
  if not sound:
    sound = permissions.get("sound",False) # TODO depricate sound
  return sound

def getWebcam(permissions):
  """ Can this program access the computer's webcam? """
  return permissions.get("webcam",False)

def getInheritWorkingDirectory(permissions):
  """ Can this program access the directory from which it was launched? """
  return permissions.get("inherit-working-directory",False)

def getAllowNetworkAccess(permissions):
  """ Can this program access the network? """
  return permissions.get("allow-network-access",False)

def getStatefulHome(permissions):
  """ Should the state of this program's home directory be saved? """
  return permissions.get("stateful-home",False)

def getAsRoot(permissions):
  """ Should this program be run as the root user WITHIN it's docker container? """
  return permissions.get("as-root",False)

def getPrivileged(permissions):
  """ Is this program to be run in privileged mode? """
  return permissions.get("privileged",False)
