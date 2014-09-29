#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import json,collections,sys,os
#internal imports
# import ...
allImagesMustHavePermissions = "All subuser images must have a permissions.json file as defined by the permissions.json standard: <https://github.com/subuser-security/subuser/blob/master/docs/permissions-dot-json-file-format.md>"

# Defaults from subuser/docs/permissions-dot-json-file-format.md
# This is a comprehensive list of all permissions
permissionDefaults = {
  "description": "" 
 ,"maintainer": ""
 ,"last-update-time": None
 ,"executable": None
 ,"shared-home": None
 ,"dependency": None
 ,"user-dirs": []
 ,"system-dirs": []
 ,"x11": False
 ,"graphics-card": False
 ,"sound-card": False
 ,"webcam": False
 ,"serial-devices":False
 ,"access-working-directory": False
 ,"allow-network-access": False
 ,"stateful-home": True
 ,"system-dbus": False
 ,"as-root": False
 ,"privileged": False
 }

def getPermissions(permissionsFilePath):
  """ Return a dictionary of permissions from the given permissions.json file.  Permissions that are not specified are set to their default values."""
  # read permissions.json file
  with open(permissionsFilePath, 'r') as file_f:
    try:
      permissions=json.load(file_f, object_pairs_hook=collections.OrderedDict)
    except ValueError:
      sys.exit(permissionsFilePath+" is not valid json.  "+allImagesMustHavePermissions)
    # Set permission defaults for permissions that are not explicitly specified in the permissions.json file
    for permission,defaultValue in permissionDefaults.iteritems():
      if not permission in permissions:
        permissions[permission] = defaultValue
    return permissions

def setPermissions(permissions,permissionsFilePath):
  """
  Save the permissions to the given file.  We only save permissions that are not set to their default values.
  """
  permissionsToSave = {}
  for permission,value in permissions.iteritems():
    if not value == permissionDefaults[permission]:
      permissionsToSave[permission] = value
  with open(permissionsFilePath, 'w') as file_f:
    json.dump(permissionsToSave,file_f,indent=1, separators=(',', ': '))

