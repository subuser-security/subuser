#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import paths
import json

def getPermissions(programName):
 """ Return the permissions for the given program. """
 # read permissions.json file
 permissionsFilePath = paths.getPermissionsFilePath(programName)
 permissionsFile = open(permissionsFilePath,"r")
 permissions=json.load(permissionsFile)
 permissionsFile.close()
 return permissions

def setPermissions(programName,permissions):
 """ Set the permissions of a given program.
 Warning, will mess up the formatting of the json file.
 """
 permissionsFilePath = paths.getPermissionsFilePath(programName)
 permissionsFile = open(permissionsFilePath,"w")
 json.dump(permissions,permissionsFile,indent=1, separators=(',', ': '))
 permissionsFile.close()
 
def hasExecutable(programName):
 """ Return True if the program has an executable associated with it. """
 try:
  getPermissions(programName)["executable"]
  return True
 except KeyError:
  return False
