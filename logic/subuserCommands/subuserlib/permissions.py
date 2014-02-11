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
