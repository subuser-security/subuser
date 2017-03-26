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

class StringToStringDict():
  pass

class StringToCommandDict():
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
#    ,("description","""Description meant to show up in standard manaual."""
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
    ,"description":"""This field describes what the subuser is/what it does.

  Ex::

    "description"                : "Simple universal text editor."
"""
    ,"default":""
    ,"types":[str]})

  ,("maintainer",
    {"describe":lambda maintainer : maintainer
    ,"description":"""This field marks who is responsible for the ``permissions.json`` file, and accompanying ``Dockerfile``.  It does NOT mark who is responsible for the image itself.

  Ex::

    ,"maintainer"                : "Timothy Hobbs <timothyhobbs (at) seznam dot cz>"
"""
    ,"default":""
    ,"types":[str]})

  ,("executable",
    {"describe":lambda executable : executable if executable else "Is a library."
    ,"description":"""This field denotes the absolute path within the Docker image where the given image's executable resides. This value is optional. if it is not present, than the subuser image cannot be run (but may be depended upon by other subuser images).

  Ex::

    ,"executable"                : "/usr/bin/vim"
"""
    ,"default":None
    ,"types":[type(None),str,ListOfStrings]})

  ,("entrypoints",
    {"describe":lambda entrypoints: "'"+ "', '".join(entrypoints.keys())+"'" if entrypoints else ""
    ,"description":"""This optional feild allows you to add "entrypoints" to your subuser. These are executables that can be added, if the user so wishes, to the PATH on the host system. This is a dictionary which maps "desired name on host" to "path within subuser image".

  Ex::

    ,"entrypoints"                : {"mk":"/usr/bin/mk","cc","/usr/local/bin/cc"}
"""
    ,"default":None
    ,"types":[type(None),StringToCommandDict]})
  ])

),(("conservative","Conservative permissions(These are safe):"),OrderedDict([

  ("basic-common-permissions",
    {"describe":lambda v: "To access basic information such as timezone and local and to save data to its own homedir." if v is True else ""
    ,"description":"""Grant access to asic information such as timezone and local and to save data to its own homedir.

  Ex::

    ,"basic-common-permissions"                : true


  Ex1::


    ,"basic-common-permissions"                : {"stateful-home":true,"inherit-timezone":false}

"""
    ,"default":False
    ,"types":[bool,OrderedDict]
    ,"subpermissions-batch-set":True
    ,"subpermissions":OrderedDict([

      ("stateful-home",
        {"describe":lambda p : "To have its own home directory where it can save files and settings." if p else ""
        ,"description":"""Changes that the subuser makes to it's home directory should be saved to a special subuser-homes directory.
"""
        ,"default":False
        ,"types":[bool]})

      ,("inherit-locale",
        {"describe":lambda p : "To find out which language you speak and what region you live in." if p else ""
        ,"description":"""Automatically set the $LANG and $LANGUAGE environment variable in the container to the value outside of the container. Note: You do not have to set this if you have set ``basic-common-permissions``.
"""
        ,"default":False
        ,"types":[bool]})

      ,("inherit-timezone",
        {"describe": lambda p : "To find out your current timezone." if p else ""
        ,"description":"""Automatically set the $TZ environment variable in the container to the value outside of the container.  Give the sub user read only access to the ``/etc/localtime`` file. Note: You do not have to set this if you have set ``basic-common-permissions``.
"""
        ,"default":False
        ,"types":[bool]})
      ])
    })

  ,("memory-limit",
    {"describe": lambda p: "Memory limited to %s"%p if p else ""
    ,"description":"""Limit subuser's available memory to this value. This is a string of format "100m" or "2g", where "m" is megabytes and "g" is gigabytes.

  Ex::

     "memory-limit":"200m"
"""
    ,"default":None
    ,"types":[type(None),str]})

  ,("max-cpus",
    {"describe":lambda p: "CPUs limited to %s"%p if p else ""
    ,"description":"""Limit number of CPUs subuser can use. This is a float.

  Ex::

    "max-cpus":2.0
"""
    ,"default":None
    ,"types":[type(None),float]})
  ])

),(("moderate","Moderate permissions(These are probably safe):"),OrderedDict([

  ("gui",
    {"describe": lambda guiOptions : "To be able to display windows." if guiOptions else ""
    ,"description":"""Is the subuser allowed to display a graphical user interface?

  Ex (enable gui, but do not enable extra fetures such as clipboard or system-tray icons)::

     "gui":true

  Ex1 (enable gui along with select features)::

    "gui":{"clipboard":true}
"""
    ,"default":False
    ,"types":[bool,OrderedDict]
    ,"conflicts":["x11"]
    ,"subpermissions": OrderedDict([

      ("clipboard",
        {"describe":lambda p : "To be able to access the host's clipboard." if p else ""
        ,"description":"""Is the subuser allowed to read and write to the clipboard?
"""
        ,"default":False
        ,"types":[bool]})

      ,("system-tray",
        {"describe":lambda p : "To be able to create system tray icons." if p else ""
        ,"description":"""Is this subuser allowed to display system-tray icons?
"""
        ,"default":False
        ,"types":[bool]})

      ,("cursors",
        {"describe":lambda p : "To be able to change the mouse's cursor icon." if p else ""
        ,"description":"""Is this subuser allowed to change the way the mouse cursor is displayed?
"""
        ,"default":False
        ,"types":[bool]})

      ,("border-color",
        {"describe":lambda p : "The border color will be "+p if p else "Warning: There will be no border coloring."
        ,"description":"""Set the border color for the window. This allows you to easily distinguish between untrusted windows and trusted ones.

  Ex (set border color to green)::

    "gui":{"border-color":"green"}

  Ex1 (display windows without adding special border color.)::

    "gui":{"border-color":nil}

"""
        ,"default":"red"
        ,"types":[type(None),str]})
      ])
    })

  ,("user-dirs",
    {"describe":lambda userDirs : "To access to the following user directories: '~/"+"' '~/".join(userDirs)+"'" if userDirs else ""
    ,"description":"""A list of relative paths to user directories which are to be shared between the host and the given image. The subuser is given read-write access to any user directories listed.

  Ex::

     ,"user-dirs"                 : ["Downloads"]

  In this example, the subuser is able to access the ``~/Downloads`` directory on the host by visiting the ``~/Userdirs/Downloads`` directory within the container.
"""
    ,"default":[]
    ,"validate": validateUserDirs
    ,"types":[ListOfStrings]})

  ,("inherit-envvars",
    {"describe":lambda envVars : "To access to the following environment variables: "+" ".join(envVars) if envVars else ""
    ,"description":"""A list of environment variables which the image will inherit from the host environment when started.

  Ex::

     ,"inherit-envvars"           : ["PGUSER","PGHOST"]
"""
    ,"default":[]
    ,"types":[ListOfStrings]})

  ,("pulseaudio",
    {"describe":lambda p : "To access to your pulseaudio server, can play sounds/record sound." if p else ""
    ,"description":"""The subuser is allowed to access the pulseaudio server on the host.

  .. warning:: This means, not only can the subuser play sounds, but it may listen to your microphone too!
"""
    ,"default":False
    ,"types":[bool]})

  ,("sound-card",
    {"describe":lambda p : "To access to your soundcard, can play sounds/record sound." if p else ""
    ,"description":"""The subuser is allowed to access the soundcard on the host.

  .. warning:: This means, not only can the subuser play sounds, but it may listen to your microphone too!
"""
    ,"default":False
    ,"types":[bool]})

  ,("webcam",
    {"describe":lambda p : "To access your computer's webcam/can see you." if p else ""
    ,"description":"""The subuser is allowed to access the computer's webcam/USB webcams.
"""
    ,"default":False
    ,"types":[bool]})

  ,("access-working-directory",
    {"describe":lambda p: "To access the directory from which it was launched." if p else ""
    ,"description":"""The subuser is given read-write access to the host user's current working directory.
"""
    ,"default":False
    ,"types":[bool]})

  ,("allow-network-access",
    {"describe":lambda p : "To access the network/internet." if p else ""
    ,"description":"""Should the subuser be allowed to access the network/internet?
"""
    ,"default":False
    ,"types":[bool]})

 ])

),(("liberal","Liberal permissions(These may pose a security risk):"),OrderedDict([

  ("x11",
    {"describe":lambda p: "To display X11 windows and interact with your X11 server directly(log keypresses, read over your shoulder, steal your passwords, control your computer ect.)" if p else ""
    ,"description":"""The subuser is allowed to interact with the x11 server on the host.

  .. note:: Known to be insecure!
"""
    ,"default":False
    ,"types":[bool]})

  ,("system-dirs",
    {"describe":lambda systemDirs : " ".join(["To read and write to the host's `"+source+"` directory, mounted in the container as:`"+dest+"`\n" for source,dest in systemDirs.items()])
    ,"description":"""A dictionary of absolute paths to directories which are to be shared between the host and the given image. The subuser is given read-write access to any user directories listed.

  Ex::

     ,"system-dirs"                 : {"/var/log":"/host/var/log"}

  In this example, the subuser is able to access the ``/var/log`` directory on the host by visiting the ``/host/var/log`` directory within the container.
"""
    ,"default":OrderedDict()
    ,"types":[StringToStringDict]})

  ,("graphics-card",
    {"describe":lambda p : "To access your graphics-card directly for OpenGL tasks." if p else "" 
    ,"description":"""The subuser is allowed to access the graphics-card directly(OpenGL).
"""
    ,"default":False
    ,"types":[bool]})

  ,("serial-devices",
    {"describe":lambda p : "To access serial devices such as programmable micro-controllers and modems." if p else ""
    ,"description":"""The subuser is allowed to access serial devices: ``/dev/ttyACM*``, ``/dev/ttyUSB*``, and ``/dev/ttyS*``.
"""
    ,"default":False
    ,"types":[bool]})

  ,("system-dbus",
    {"describe":lambda p: "To talk to the system dbus daemon." if p else ""
    ,"description":"""Should the subuser be allowed to communicate with the system wide dbus daemon?
"""
    ,"default":False
    ,"types":[bool]})

  ,("sudo",
    {"describe": lambda p: "To be allowed to use the sudo command to run subproccesses as root in the container." if p else ""
    ,"description":"""Grant the subuser sudo privileges within the container.
"""
    ,"default":False
    ,"types":[bool]})

  ,("as-root",
    {"describe": lambda p: "To be allowed to run as root within the container." if p else ""
    ,"description":"""Run the subuser as the root user within the container.
"""
    ,"default":False
    ,"types":[bool]})

  ])

),(("anarchistic","Anarchistic permissions\n   WARNING: These permissions give the subuser full access to your system when run."),OrderedDict([
 
  ("privileged",
    {"describe": lambda p: "To have full access to your system.  To even do things as root outside of its container." if p else ""
    ,"description":"""Should the subuser's Docker container be run in ``privileged`` mode?

  .. warning:: Completely insecure!
"""
    ,"default":False
    ,"types":[bool]})

  ,("run-commands-on-host",
    {"describe": lambda p: "To run commands as a normal user on the host system." if p else ""
    ,"description":"""Should the subuser be able to execute commands as the normal user on the host system? If this is enabled, a ``/subuser/execute`` file will be present in the container. Any text appended to this file will be piped to ``/bin/sh`` on the host machine.

  .. warning:: Obviously completely compromises security.
"""
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

def getTypeDescriptions(types):
  typeDescriptions = {
    str:"string"
   ,type(None):"nil"
   ,bool:"bool"
   ,float:"floating point number"
   ,ListOfStrings:"List of strings"
   ,StringToStringDict:"Dict of strings."
   ,StringToCommandDict:"Dict mapping names to commands."
   ,OrderedDict: "set of subpermissions"}
  typestrings = []
  for t in types:
    if t in typeDescriptions:
      typestrings.append(typeDescriptions[t])
    else:
      typestrings.append(str(t))
  return typestrings

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
      elif type(value) == OrderedDict and (StringToStringDict in types or StringToCommandDict in types):
        for s in value.values():
          if not type(s) == str:
            if type(s) == list and StringToCommandDict in types:
              continue
            raise SyntaxError("Permission "+permission+" set to invalid value <"+str(value)+">. Expected a string to string dictionary.")
      else:
        typestrings = getTypeDescriptions(types)
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
  Analize permission dictionaries for changes.
  First, compare the old defaults to the user approved permissions.
  By doing so, we aquire an understanding of which permissions have been set by the user, and which are still at their default values.
  We will leave the user-set permissions alone.

  Next, we compare the old non-user set permissions to the new defaults.

  The return value is a tuple of the form: ([removed-permisions],{additions/changes})
  """
  return __compare(oldDefaults = getNonDefaultPermissions(oldDefaults), newDefaults = getNonDefaultPermissions(newDefaults), userApproved = getNonDefaultPermissions(userApproved))

def __compare(oldDefaults,newDefaults,userApproved):
  """
  >>> import subuserlib.permissions
  >>> subuserlib.permissions.__compare(oldDefaults={"a":1,"b":2,"c":3,"d":4,"e":5},newDefaults={"a":1,"b":3,"c":4,"f":4},userApproved={"a":1,"b":5,"e":5,"z":7}) == (["e"],{"f":4})
  True

  If the permissions contain an OrderedDict subgroup where the order doesn't match, the comparison still works.

  >>> from collections import OrderedDict
  >>> subuserlib.permissions.__compare(oldDefaults={"a":1,"b":2,"c":3,"d":4,"e":5,"g":OrderedDict([("a",1),("b",2)])},newDefaults={"a":1,"b":3,"c":4,"f":4,"g":OrderedDict([("b",2),("a",1)])},userApproved={"a":1,"b":5,"e":5,"z":7,"g":OrderedDict([("a",1),("b",2)])}) == (["e"],{"f":4})
  True
  >>> subuserlib.permissions.__compare(oldDefaults={"a":1,"b":2,"c":3,"d":4,"e":5,"g":OrderedDict([("a",1),("b",2)])},newDefaults={"a":1,"b":3,"c":4,"f":4,"g":OrderedDict([("b",3),("a",1)])},userApproved={"a":1,"b":5,"e":5,"z":7,"g":OrderedDict([("a",1),("b",2)])}) == (["e"],{"f":4,"g":OrderedDict([("b",3),("a",1)])})
  True
  """
  def neq(a,b):
    if type(a) == type(b) and type(a) == OrderedDict:
      if len(a) != len(b):
        return True
      for key,value in a.items():
        if b[key] != value:
          return True
      return False
    else:
      return a != b
  # This set is the union of the user approved permissions
  userChangedPermissions = set()
  for key,value in userApproved.items():
    try:
      if neq(oldDefaults[key],value):
        userChangedPermissions.add(key)
    except KeyError:
      userChangedPermissions.add(key)
  userDeniedPermissions = set()
  for key,value in oldDefaults.items():
    if (not key in userApproved):
      userDeniedPermissions.add(key)
  userSetPermissions = userChangedPermissions.union(userDeniedPermissions)
  addedOrChangedPermissions = {}
  for key,value in newDefaults.items():
    #                                                         added  or  changed
    if (not key in userSetPermissions) and ((not key in oldDefaults) or (key in oldDefaults and neq(oldDefaults[key],value))):
      addedOrChangedPermissions[key] = value
  droppedPermissions = []
  for key in oldDefaults.keys():
    if (key not in userSetPermissions) and (key not in newDefaults):
      droppedPermissions.append(key)
  return (droppedPermissions,addedOrChangedPermissions)

docs_header = """The permissions.json file format
================================

A permissions.json file is a file which describes the rights or permissions of a given subuser.  These permissions pertain mainly to that image's ability to interact with it's host operating system.

Each permissions.json file is to be a valid `json <https://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf>`_ file containing a single json object.

All permissions are optional. If they are not included in the ``permissions.json`` file, than they are set to their default (and most restrictive) setting.

Setting a permission to an empty string is not a valid way of requesting it's default value.  If you want the default value, don't include the permission at all.

Permissions are categorized into 4 levels of permissiveness:

 1. conservative: These permissions should be 100% safe in all cases.
 2. moderate: These permissions have the potential to give the subuser access to some user data but not all.
 3. liberal: These permissions give the subuser access to some or all user data, and/or present a significantly increased risk of the subuser breaking out of the container.
 4. anarchistic: These permissions give the subuser full access to the system.

"""

depricatedPermissions = """
Depricated
----------

These permissions can still be used as top level permissions. However, they have now been rolled in as subpermissions to ``basic-common-permissions``.

 * ``stateful-home``: Changes that the subuser makes to it's home directory should be saved to a special subuser-homes directory.

  **Default**: ``false``

 * ``inherit-locale``: Automatically set the $LANG and $LANGUAGE environment variable in the container to the value outside of the container. Note: You do not have to set this if you have set ``basic-common-permissions``.

  **Default**: ``false``

 * ``inherit-timezone``: Automatically set the $TZ environment variable in the container to the value outside of the container.  Give the sub user read only access to the ``/etc/localtime`` file. Note: You do not have to set this if you have set ``basic-common-permissions``.

  **Default**: ``false``
"""

def get_default_description(default):
  default_descriptions = {
    "" : '""'
    ,True:"true"
    ,False:"false"
    ,None:"nil"
    ,OrderedDict:"{}"}
  try:
    return default_descriptions[default]
  except (KeyError,TypeError):
    try:
      return default_descriptions[type(default)]
    except KeyError:
      return str(default)

def get_permission_description(indent1,indent2,permission,permission_attrs):
  docs = ""
  try:
    docs += indent1+" ``"+permission+"``: "+permission_attrs["description"].replace("\n","\n"+indent2)+"\n"
  except KeyError:
    docs += indent1+" ``"+permission+"``:\n"
  docs += indent2+"Default: ``"+get_default_description(permission_attrs["default"])+"``\n\n"
  docs += indent2+"Types: ``"+"``, ``".join(getTypeDescriptions(permission_attrs["types"]))+"``\n\n"
  return docs


def getDocs():
  docs = docs_header
  for (level,level_description),permissions in supportedPermissions.items():
    docs += level_description+"\n"
    docs += "-"*len(level_description)+"\n"
    for permission,permission_attrs in permissions.items():
      docs += get_permission_description(" *","  ",permission,permission_attrs)
      if "subpermissions" in permission_attrs:
        docs += "  ``"+permission+"`` **subpermissions:**\n\n"
        for subpermission,subpermission_attrs in permission_attrs["subpermissions"].items():
          docs += get_permission_description("   -","    ",subpermission,subpermission_attrs)
  docs += depricatedPermissions
  return docs
