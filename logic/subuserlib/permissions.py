#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
Module used for the loading and saving of permissions.json files. Contains the default permissions list.
"""

#external imports
import json,collections,sys,os
#internal imports
# import ...
allImagesMustHavePermissions = "All subuser images must have a permissions.json file as defined by the permissions.json standard: <https://github.com/subuser-security/subuser/blob/master/docs/permissions-dot-json-file-format.md>"

# Defaults from subuser/docs/permissions-dot-json-file-format.md
# This is a comprehensive list of all permissions
permissionDefaults = {
 # Conservative permissions
  "description": ""
 ,"maintainer": ""
 ,"last-update-time": None
 ,"executable": None
 ,"basic-common-permissions": False
 ,"stateful-home": False
 ,"inherit-locale": False
 ,"inherit-timezone": False
 # Moderate permissions
 ,"gui": None
 ,"user-dirs": []
 ,"inherit-envvars": []
 ,"sound-card": False
 ,"webcam": False
 ,"access-working-directory": False
 ,"allow-network-access": False
 # Liberal permissions
 ,"x11": False
 ,"system-dirs": {}
 ,"graphics-card": False
 ,"serial-devices":False
 ,"system-dbus": False
 ,"as-root": False
 ,"sudo": False
 # Anarchistic permissions
 ,"privileged": False
 }

guiPermissionDefaults = {
 "clipboard": False,
 "system-tray": False,
 "cursors": False
 }

basicCommonPermissions = ["stateful-home","inherit-locale","inherit-timezone"]

def getPermissions(permissionsFilePath):
  """ Return a dictionary of permissions from the given permissions.json file.  Permissions that are not specified are set to their default values."""
  # read permissions.json file
  with open(permissionsFilePath, 'r') as file_f:
    try:
      permissions=json.load(file_f, object_pairs_hook=collections.OrderedDict)
    except ValueError:
      sys.exit(permissionsFilePath+" is not valid json.  "+allImagesMustHavePermissions)
    # Validate that the permissions are supported by this version of subuser.
    for permission in permissions.keys():
      if not permission in permissionDefaults:
         sys.exit("Error: the permission \""+permission+"\" is not supported by your version of subuser.  Try updating first.")
    if "gui" in permissions and not permissions["gui"] is None:
      for guiPermission in permissions["gui"].keys():
       if not guiPermission in guiPermissionDefaults:
         sys.exit("Error: the gui permission \""+guiPermission+"\" is not supported by your version of subuser.  Try updating first.")
    # Set permission defaults for permissions that are not explicitly specified in the permissions.json file
    if "basic-common-permissions" in permissions and permissions["basic-common-permissions"]:
      for basicCommonPermission in basicCommonPermissions:
        if not basicCommonPermission in permissions:
          permissions[basicCommonPermission] = True
    for permission,defaultValue in permissionDefaults.items():
      if not permission in permissions:
        permissions[permission] = defaultValue
    # gui permissions
    if not permissions["gui"] is None:
      for permission,defaultValue in guiPermissionDefaults.items():
        if not permission in permissions["gui"]:
          permissions["gui"][permission] = defaultValue
  
    return permissions

def getPermissonsJSONString(permissions):
  """
  Returns the given permissions as a JSON formated string.
  """
  permissionsToSave = {}
  for permission,value in permissions.items():
    if not value == permissionDefaults[permission]:
      permissionsToSave[permission] = value
  return json.dumps(permissionsToSave,indent=1, separators=(',', ': '))


def setPermissions(permissions,permissionsFilePath):
  """
  Save the permissions to the given file.  We only save permissions that are not set to their default values.
  """
  try:
    dir,_ = os.path.split(permissionsFilePath)
    os.makedirs(dir)
  except OSError:
    pass
  with open(permissionsFilePath, 'w') as file_f:
    file_f.write(getPermissonsJSONString(permissions))

