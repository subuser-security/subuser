# -*- coding: utf-8 -*-

"""
Module used for the loading and saving of permissions.json files. Contains the default permissions list.
"""

#external imports
import json
from collections import OrderedDict
import sys
import os
import copy
#internal imports
# import ...
allImagesMustHavePermissions = "All subuser images must have a permissions.json file as defined by the permissions.json standard: <http://subuser.org/subuser-standard/permissions-dot-json-file-format.html>"

class ListOfStrings():
  pass

def validateUserDirs(userDirs):
  for userDir in userDirs:
    if ".." in userDir or userDir.startswith("./"):
      raise SyntaxError("Error, user dir permissions may not contain relative paths. The user dir: \""+userDir+"\" is forbidden.")
    if userDir.startswith("/"):
      raise SyntaxError("Error, user dir permissions may not contain system wide absolute paths. The user dir: \""+userDir+"\" is forbidden.")

# Defaults from http://subuser.org/subuser-standard/permissions-dot-json-file-format.html
# This is a comprehensive list of all permissions
supportedPermissions = OrderedDict([
#The format of this dictionary is
#(NAME_OF_DANGER_LEVEL,DESCRIPTION_OF_DANGER_LEVEL):
#  [("<name-of-permission>",
#    [("describe",<lambda that generates english langauge description of permission, given its value.>)
#    ,("default",<default value of permission>)
#    ,("types",[<valid types that the permissions value can have, used for permission file validation>])
#    OPTIONALLY
#    ,("subpermissions",
#      [
#      <same format as for top level permissions>
#      ]
#    ,("conflicts",[<permissions that cannot be granted at the same time as this permission>])
#    ]
#  ]

(("prelude","Prelude:"),

  OrderedDict([("description",
    {"describe":lambda v: v
    ,"default":""
    ,"types":[str]})

  ,("maintainer",
    {"describe":lambda maintainer : maintainer
    ,"default":""
    ,"types":[str]})

  ,("executable",
    {"describe":lambda executable : executable if executable else "Is a library."
    ,"default":None
    ,"types":[type(None),str]})

  ,("entrypoints",
    {"describe":lambda entrypoints: "'"+ "', '".join(entrypoints.keys())+"'" if entrypoints else ""
    ,"default":None
    ,"types":[type(None),OrderedDict]})
  ])

),(("conservative","Conservative permissions(These are safe):"),OrderedDict([

  ("basic-common-permissions",
    {"describe":lambda v: "To access basic information such as timezone and local and to save data to its own homedir." if v is True else ""
    ,"default":False
    ,"types":[bool,OrderedDict]
    ,"subpermissions-batch-set":True
    ,"subpermissions":OrderedDict([

      ("stateful-home",
        {"describe":lambda p : "To have its own home directory where it can save files and settings." if p else ""
        ,"default":False
        ,"types":[bool]})

      ,("inherit-locale",
        {"describe":lambda p : "To find out which language you speak and what region you live in." if p else ""
        ,"default":False
        ,"types":[bool]})

      ,("inherit-timezone",
        {"describe": lambda p : "To find out your current timezone." if p else ""
        ,"default":False
        ,"types":[bool]})
      ])
    })

  ,("memory-limit",
    {"describe": lambda p: "Memory limited to %s"%p if p else ""
    ,"default":None
    ,"types":[type(None),str]})

  ,("max-cpus",
    {"describe":lambda p: "CPUs limited to %s"%p if p else ""
    ,"default":None
    ,"types":[type(None),float]})
  ])

),(("moderate","Moderate permissions(These are probably safe):"),OrderedDict([

  ("gui",
    {"describe": lambda guiOptions : "To be able to display windows." if guiOptions else ""
    ,"default":False
    ,"types":[bool,OrderedDict]
    ,"conflicts":["x11"]
    ,"subpermissions": OrderedDict([

      ("clipboard",
        {"describe":lambda p : "To be able to access the host's clipboard." if p else ""
        ,"default":False
        ,"types":[bool]})

      ,("system-tray",
        {"describe":lambda p : "To be able to create system tray icons." if p else ""
        ,"default":False
        ,"types":[bool]})

      ,("cursors",
        {"describe":lambda p : "To be able to change the mouse's cursor icon." if p else ""
        ,"default":False
        ,"types":[bool]})
      ])
    })

  ,("user-dirs",
    {"describe":lambda userDirs : "To access to the following user directories: '~/"+"' '~/".join(userDirs)+"'" if userDirs else ""
    ,"default":[]
    ,"validate": validateUserDirs
    ,"types":[ListOfStrings]})

  ,("inherit-envvars",
    {"describe":lambda envVars : "To access to the following environment variables: "+" ".join(envVars) if envVars else ""
    ,"default":[]
    ,"types":[ListOfStrings]})

  ,("sound-card",
    {"describe":lambda p : "To access to your soundcard, can play sounds/record sound." if p else ""
    ,"default":False
    ,"types":[bool]})

  ,("webcam",
    {"describe":lambda p : "To access your computer's webcam/can see you." if p else ""
    ,"default":False
    ,"types":[bool]})

  ,("access-working-directory",
    {"describe":lambda p: "To access the directory from which it was launched." if p else ""
    ,"default":False
    ,"types":[bool]})

  ,("allow-network-access",
    {"describe":lambda p : "To access the network/internet." if p else ""
    ,"default":False
    ,"types":[bool]})

 ])

),(("liberal","Liberal permissions(These may pose a security risk):"),OrderedDict([

  ("x11",
    {"describe":lambda p: "To display X11 windows and interact with your X11 server directly(log keypresses, read over your shoulder, steal your passwords, control your computer ect.)" if p else ""
    ,"default":False
    ,"types":[bool]})

  ,("system-dirs",
    {"describe":lambda systemDirs : " ".join(["To read and write to the host's `"+source+"` directory, mounted in the container as:`"+dest+"`\n" for source,dest in systemDirs.items()])
    ,"default":OrderedDict()
    ,"types":[OrderedDict]})

  ,("graphics-card",
    {"describe":lambda p : "To access your graphics-card directly for OpenGL tasks." if p else "" 
    ,"default":False
    ,"types":[bool]})

  ,("serial-devices",
    {"describe":lambda p : "To access serial devices such as programmable micro-controllers and modems." if p else ""
    ,"default":[]
    ,"types":[ListOfStrings]})

  ,("system-dbus",
    {"describe":lambda p: "To talk to the system dbus daemon." if p else ""
    ,"default":False
    ,"types":[bool]})

  ,("sudo",
    {"describe": lambda p: "To be allowed to use the sudo command to run subproccesses as root in the container." if p else ""
    ,"default":False
    ,"types":[bool]})

  ,("as-root",
    {"describe": lambda p: "To be allowed to run as root within the container." if p else ""
    ,"default":False
    ,"types":[bool]})

  ])

),(("anarchistic","WARNING: These permissions give the subuser full access to your system when run."),OrderedDict([
 
  ("privileged",
    {"describe": lambda p: "To have full access to your system.  To even do things as root outside of its container." if p else ""
    ,"default":False
    ,"types":[bool]})

  ,("run-commands-on-host",
    {"describe": lambda p: "To run commands as a normal user on the host system." if p else ""
    ,"default":False
    ,"types":[bool]})

  ])
)])

def getDefaults():
  default_permissions = OrderedDict()
  for level,permissions in supportedPermissions.items():
    for permission,value in permissions.items():
      default_permissions[permission] = copy.deepcopy(value["default"])
  return default_permissions

basicCommonPermissions = ["stateful-home","inherit-locale","inherit-timezone"]

def load(permissionsFilePath=None,permissionsString=None, logger = None):
  """
  Return a dictionary of permissions from the given permissions.json file.  Permissions that are not specified are set to their default values.

  Loading permissions doesn't crash horribly and does something at least slightly sensible.

  >>> getNonDefaultPermissions(load(permissionsString="{}"))
  OrderedDict()

  Valid paths are loaded when the user-dirs permission is set.

  >>> print(json.dumps(getNonDefaultPermissions(load(permissionsString='{\"user-dirs\":[\"Downloads\"]}'))))
  {"user-dirs": ["Downloads"]}

  However, funny business is strictly frowned upon.

  >>> getNonDefaultPermissions(load(permissionsString='{\"user-dirs\":[\"..\"]}'))
  Traceback (most recent call last):
    ...
  SyntaxError: Error, user dir permissions may not contain relative paths. The user dir: ".." is forbidden.

  >>> getNonDefaultPermissions(load(permissionsString='{\"user-dirs\":[\"../\"]}'))
  Traceback (most recent call last):
    ...
  SyntaxError: Error, user dir permissions may not contain relative paths. The user dir: "../" is forbidden.

  >>> getNonDefaultPermissions(load(permissionsString='{\"user-dirs\":[\"./../../\"]}'))
  Traceback (most recent call last):
    ...
  SyntaxError: Error, user dir permissions may not contain relative paths. The user dir: "./../../" is forbidden.

  Even if it is well hiden behind valid values.

  >>> getNonDefaultPermissions(load(permissionsString='{\"user-dirs\":[\"Downloads\",\"../\"]}'))
  Traceback (most recent call last):
    ...
  SyntaxError: Error, user dir permissions may not contain relative paths. The user dir: "../" is forbidden.

  >>> getNonDefaultPermissions(load(permissionsString='{\"user-dirs\":[\"Downloads\",\"./Foo\"]}'))
  Traceback (most recent call last):
    ...
  SyntaxError: Error, user dir permissions may not contain relative paths. The user dir: "./Foo" is forbidden.

  >>> getNonDefaultPermissions(load(permissionsString='{\"user-dirs\":[\"Downloads\",\"/Foo\"]}'))
  Traceback (most recent call last):
    ...
  SyntaxError: Error, user dir permissions may not contain system wide absolute paths. The user dir: "/Foo" is forbidden.

  >>> getNonDefaultPermissions(load(permissionsString='{\"x11\":true,\"gui\":true}'))
  Traceback (most recent call last):
    ...
  SyntaxError: x11 and gui permissions are mutually exclusive.

  """
  if not permissionsString is None:
    try:
      loading=json.loads(permissionsString, object_pairs_hook=OrderedDict)
    except ValueError:
      sys.exit(permissionsString+" is not valid json.  "+allImagesMustHavePermissions)
  else:
    # read permissions.json file
    with open(permissionsFilePath, 'r') as file_f:
      try:
        loading=json.load(file_f, object_pairs_hook=OrderedDict)
      except ValueError:
        raise SyntaxError(permissionsFilePath+" is not valid json.  "+allImagesMustHavePermissions)
  def validate(permission,value,attrs):
    types = attrs["types"]
    if not type(value) in types:
      if type(value) == list and ListOfStrings in types:
        for s in value:
          if not type(s) == str:
            raise SyntaxError("Permission "+permission+" set to invalid value <"+str(value)+">. Expected a list of strings.")
      else:
        typeDescriptions = {
          str:"string"
         ,type(None):"nil"
         ,float:"floating point number"
         ,OrderedDict: "set of subpermissions"}
        typestrings = []
        for t in types:
          if t in typeDescriptions:
            typestrings.append(typeDescriptions[t])
          else:
            typestrings.append(str(t))
        raise SyntaxError("Permisison "+permission+" set to invalid value <"+str(value)+">. Expected "+" or ".join(typestrings))
    if "validate" in attrs:
      attrs["validate"](value)
 
  # Validate that the permissions are supported by this version of subuser.
  loadedPermissions = OrderedDict()
  for level,permissions in supportedPermissions.items():
    for permission,attributes in permissions.items():
      loadedPermissions[permission] = attributes["default"]
      if permission in loading:
        try:
          loading_permission = loading[permission]
        except KeyError:
          continue
        validate(permission,loading_permission,attributes)
        if "conflicts" in attributes:
          for conflict in attributes["conflicts"]:
            if conflict in loading and loading[conflict] and loading_permission:
              raise SyntaxError(conflict+" and "+permission+" permissions are mutually exclusive.")
        if "subpermissions" in attributes and loading_permission:
          loadedPermissions[permission] = OrderedDict()
          for subpermission,subattrs in attributes["subpermissions"].items():
            loadedPermissions[permission][subpermission] = subattrs["default"] #TODO DRY
            if type(loading_permission) == OrderedDict:
              try:
                loading_subpermission = loading_permission[subpermission]
              except KeyError:
                continue
              validate(permission+"."+subpermission,loading_subpermission,subattrs)
              loadedPermissions[permission][subpermission] = loading_subpermission
            elif type(loading_permission) == bool:
              if "subpermissions-batch-set" in attributes and attributes["subpermissions-batch-set"]:
                loadedPermissions[permission][subpermission] = loading_permission
              else:
                loadedPermissions[permission][subpermission] = subattrs["default"]
        else:
          loadedPermissions[permission] = loading_permission
  for permission,value in loading.items():
    if permission not in loadedPermissions and permission not in basicCommonPermissions:
      if logger is not None:
        logger.log("Permission "+permission+" is not supported by this version of subuser.")
  return loadedPermissions

def getNonDefaultPermissions(permissions):
  """
  Returns the dictionary of permissions which are NOT set to their default values.

  >>> import subuserlib.permissions
  >>> permissions = subuserlib.permissions.load(permissionsString='{"x11":true}')
  >>> getNonDefaultPermissions(permissions) == {u'x11': True}
  True
  """
  nonDefaultPermissions = OrderedDict()
  defaults = getDefaults()
  for permission,value in permissions.items():
    if not value == defaults[permission]:
      nonDefaultPermissions[permission] = value
  return nonDefaultPermissions

def getJSONString(permissions):
  """
  Returns the given permissions as a JSON formated string.
  """
  permissionsToSave = getNonDefaultPermissions(permissions)
  return json.dumps(permissionsToSave,indent=1, separators=(',', ': '))

def getDescription(permissionsToDescribe):
  descriptionTemplate = {
    "level_heading":" %s"
   ,"permission_description":"  - %s: %s"
   ,"sub_permission_description":"   * %s"
   }
  description = []
  for (level,levelDescription),permissions in supportedPermissions.items():
    descriptionForThisLevel = []
    describedSomething = False
    descriptionForThisLevel.append(descriptionTemplate["level_heading"]%levelDescription)
    for permission,attributes in permissions.items():
      try:
        permissionValue = permissionsToDescribe[permission]
      except KeyError:
        continue
      if permissionValue:
        describedSomething = True
        descriptionForThisLevel.append(descriptionTemplate["permission_description"]%(permission,attributes["describe"](permissionValue)))
        if "subpermissions" in attributes and type(permissionValue) == OrderedDict:
          for subpermission,subattributes in attributes["subpermissions"].items():
            if permissionValue[subpermission]:
              descriptionForThisLevel.append(descriptionTemplate["sub_permission_description"]%subattributes["describe"](permissionValue[subpermission]))
    if describedSomething:
      description += descriptionForThisLevel
  return "\n".join(description)


def compare(oldDefaults,newDefaults,userApproved):
  """
  Analize permission sets for changes.
  First, compare the old defaults to the user approved permissions.
  By doing so, we aquire an understanding of which permissions have been set by the user, and which are still at their default values.
  We will leave the user-set permissions alone.

  Next, we compair the old non-user set permissions to the new defaults.

  Finally, we return a list of permissions that have been removed as well as a dictionary of permissions which have been added or changed.

  The return value is a tuple of the form: ([removed-permisions],{additions/changes})
  """
  return __compare(oldDefaults = getNonDefaultPermissions(oldDefaults), newDefaults = getNonDefaultPermissions(newDefaults), userApproved = getNonDefaultPermissions(userApproved))

def __compare(oldDefaults,newDefaults,userApproved):
  """
  Analize permission sets for changes.
  First, compare the old defaults to the user approved permissions.
  By doing so, we aquire an understanding of which permissions have been set by the user, and which are still at their default values.
  We will leave the user-set permissions alone.

  Next, we compair the old non-user set permissions to the new defaults.

  Finally, we return a list of permissions that have been removed as well as a dictionary of permissions which have been added or changed.

  >>> import subuserlib.permissions
  >>> subuserlib.permissions.__compare(oldDefaults={"a":1,"b":2,"c":3,"d":4,"e":5},newDefaults={"a":1,"b":3,"c":4,"f":4},userApproved={"a":1,"b":5,"e":5,"z":7}) == (["e"],{"f":4})
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
