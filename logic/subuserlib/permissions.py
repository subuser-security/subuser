#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
Module used for the loading and saving of permissions.json files. Contains the default permissions list.
"""

#external imports
import json
import collections
import sys
import os
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

levels = [
  {"name" : "prelude",
   "permissions" : ["description", "maintainer", "executable"],
   "description" : ""},
  {"name" : "conservative",
   "permissions" : ["stateful-home", "inherit-locale", "inherit-timezone"],
   "description" : "Conservative permissions(These are safe):"},
  {"name" : "moderate",
   "permissions" : ["gui", "user-dirs", "sound-card", "webcam", "access-working-directory", "allow-network-access"],
   "description" : "Moderate permissions(These are probably safe):"},
  {"name" : "liberal",
   "permissions" : ["x11", "system-dirs", "graphics-card", "serial-devices", "system-dbus", "as-root"],
   "description" : "Liberal permissions(These may pose a security risk):"},
  {"name" : "anarchistic",
   "permissions" : ["privileged"],
   "description" : "WARNING: These permissions give the subuser full access to your system when run."}]

permissionDescriptions = {
  # Prelude
  "description":lambda description : ["Description: "+description]
  ,"maintainer":lambda maintainer : ["Maintainer: "+maintainer]
  ,"executable":lambda executable : ["Executable: "+executable] if executable else ["Is a library."]
  # Conservative
  ,"stateful-home": lambda p : ["To have its own home directory where it can save files and settings."] if p else []
  ,"inherit-locale": lambda p : ["To find out language you speak and what region you live in."] if p else []
  ,"inherit-timezone": lambda p : ["To find out your current timezone."] if p else []
  # Moderate
  ,"gui": lambda guiOptions : (["To be able to display windows."] + sum([guiPermissionDescriptions[permission](value) for permission,value in guiOptions.items()],[])) if guiOptions else []
  ,"user-dirs": lambda userDirs : ["To access to the following user directories: '~/"+"' '~/".join(userDirs)+"'"] if userDirs else []
  ,"inherit-envvars": lambda envVars : ["To access to the following environment variables: "+" ".join(envVars)] if envVars else []
  ,"sound-card": lambda p : ["To access to your soundcard, can play sounds/record sound."] if p else []
  ,"webcam": lambda p : ["To access your computer's webcam/can see you."] if p else []
  ,"access-working-directory": lambda p: ["To access the directory from which it was launched."] if p else []
  ,"allow-network-access": lambda p : ["To access the network/internet."] if p else []
  # Liberal
  ,"x11": lambda p : ["To display X11 windows and interact with your X11 server directly(log keypresses, read over your shoulder, steal your passwords, controll your computer ect.)"] if p else []
  ,"system-dirs": lambda systemDirs : ["To read and write to the host's `"+source+"` directory, mounted in the container as:`"+dest+"`" for source,dest in systemDirs.items()]
  ,"graphics-card": lambda p : ["To access your graphics-card directly for OpenGL tasks."] if p else []
  ,"serial-devices": lambda p : ["To access serial devices such as programable micro-controlers and modems."] if p else []
  ,"system-dbus": lambda p: ["To talk to the system dbus daemon."] if p else []
  ,"sudo": lambda p: ["To be allowed to use the sudo command to run subproccesses as root in the container."] if p else []
  ,"as-root": lambda p: ["To be allowed to run as root within the container."] if p else []
  # Anarchistic
  ,"privileged": lambda p: ["To have full access to your system.  To even do things as root outside of its container."] if p else []
  }

guiPermissionDescriptions = {
  "clipboard": lambda p : ["Is able to access the host's clipboard."] if p else []
  ,"system-tray": lambda p : ["Is able to create system tray icons."] if p else []
  ,"cursors": lambda p : ["Is able to change the mouse's cursor icon."] if p else []}

def getPermissions(permissionsFilePath=None,permissionsString=None):
  """
  Return a dictionary of permissions from the given permissions.json file.  Permissions that are not specified are set to their default values.
  """
  if not permissionsString is None:
    try:
      permissions=json.loads(permissionsString, object_pairs_hook=collections.OrderedDict)
    except ValueError:
      sys.exit(permissionsString+" is not valid json.  "+allImagesMustHavePermissions)
  else:
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

def getNonDefaultPermissions(permissions):
  """
  Returns the dictionary of permissions which are NOT set to their default values.

  >>> import subuserlib.permissions
  >>> permissions = subuserlib.permissions.getPermissions(permissionsString='{"x11":true}')
  >>> getNonDefaultPermissions(permissions) == {u'x11': True}
  True
  """
  nonDefaultPermissions = collections.OrderedDict()
  for permission,value in permissions.items():
    if not value == permissionDefaults[permission]:
      nonDefaultPermissions[permission] = value
  return nonDefaultPermissions

def getPermissonsJSONString(permissions):
  """
  Returns the given permissions as a JSON formated string.
  """
  permissionsToSave = getNonDefaultPermissions(permissions)
  return json.dumps(permissionsToSave,indent=1, separators=(',', ': '))

def setPermissions(permissions,permissionsFilePath):
  """
  Save the permissions to the given file.  We only save permissions that are not set to their default values.
  """
  try:
    directory,_ = os.path.split(permissionsFilePath)
    os.makedirs(directory)
  except OSError:
    pass
  with open(permissionsFilePath, 'w') as file_f:
    file_f.write(getPermissonsJSONString(permissions))

def comparePermissions(oldDefaults,newDefaults,userApproved):
  """
  Analize permission sets for changes.
  First, compare the old defaults to the user approved permissions.
  By doing so, we aquire an understanding of which permissions have been set by the user, and which are still at their default values.
  We will leave the user-set permissions alone.

  Next, we compair the old non-user set permissions to the new defaults.

  Finally, we return a list of permissions that have been removed as well as a dictionary of permissions which have been added or changed.

  The return value is a tuple of the form: ([removed-permisions],{additions/changes})
  """
  return __comparePermissions(oldDefaults = getNonDefaultPermissions(oldDefaults), newDefaults = getNonDefaultPermissions(newDefaults), userApproved = getNonDefaultPermissions(userApproved))

def __comparePermissions(oldDefaults,newDefaults,userApproved):
  """
  Analize permission sets for changes.
  First, compare the old defaults to the user approved permissions.
  By doing so, we aquire an understanding of which permissions have been set by the user, and which are still at their default values.
  We will leave the user-set permissions alone.

  Next, we compair the old non-user set permissions to the new defaults.

  Finally, we return a list of permissions that have been removed as well as a dictionary of permissions which have been added or changed.

  >>> import subuserlib.permissions
  >>> subuserlib.permissions.__comparePermissions(oldDefaults={"a":1,"b":2,"c":3,"d":4,"e":5},newDefaults={"a":1,"b":3,"c":4,"f":4},userApproved={"a":1,"b":5,"e":5,"z":7}) == (["e"],{"f":4})
  True
  """
  userSetPermissions = {}
  for key,value in userApproved.items():
    # Cleaver code is evil, but I have given into temptation in this case ^_^
    if (not key in oldDefaults) or (oldDefaults[key] != value):
      userSetPermissions[key] = value
  for key,value in oldDefaults.items():
    if (not key in userApproved):
      userSetPermissions[key] = value
  addedOrChangedPermissions = {}
  for key,value in newDefaults.items():
    #                                                         added  or  changed
    if (not key in userSetPermissions) and ((not key in oldDefaults) or (key in oldDefaults and oldDefaults[key] != value)):
      addedOrChangedPermissions[key] = value
  droppedPermissions = []
  for key in oldDefaults.keys():
    if (key not in userSetPermissions) and (key not in newDefaults):
      droppedPermissions.append(key)
  return (droppedPermissions,addedOrChangedPermissions)
