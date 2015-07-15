#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
Each subuser has a set of permissions which specify what parts of the host system it is allowed to access.
"""

#external imports
import collections,hashlib
#internal imports
import subuserlib.classes.userOwnedObject,subuserlib.classes.fileBackedObject,subuserlib.permissions

class Permissions(collections.OrderedDict,subuserlib.classes.userOwnedObject.UserOwnedObject,subuserlib.classes.fileBackedObject.FileBackedObject):
  __writePath = None

  def __init__(self,user,readPath,writePath):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    collections.OrderedDict.__init__(self)
    self.__writePath = writePath
    self.update(subuserlib.permissions.getPermissions(readPath))

  def getWritePath(self):
    """
    Return the path to which the permissions object is to be saved.
    """
    return self.__writePath

  def getHash(self):
    """
    Return the SHA512 hash of the given permissions.
    """
    hasher = hashlib.sha512()
    hasher.update(subuserlib.permissions.getPermissonsJSONString(self).encode('utf-8'))
    return hasher.hexdigest()

  def save(self):
    subuserlib.permissions.setPermissions(self,self.__writePath)

  def describe(self):
    print(" Description: "+self["description"])
    print(" Maintainer: "+self["maintainer"])
    print(" Last update time(version): "+str(self["last-update-time"]))
    if self["executable"]:
      print(" Executable: "+self["executable"])
    else:
      print(" Is a library")

    def areAnyOfThesePermitted(permissions):
      permitted = False
      for permission in permissions:
        if self[permission]:
          permitted = True
      return permitted

    conservativePermissions = ["stateful-home","inherit-locale","inherit-timezone"]
    if areAnyOfThesePermitted(conservativePermissions):
      print(" Conservative permissions(These are safe):")
      if self["stateful-home"]:
        print("  Has it's own home directory where it can save files and settings.")
      if self["inherit-locale"]:
        print("  Can find out language you speak and what region you live in.")
      if self["inherit-timezone"]:
        print("  Can find out your current timezone.")

    moderatePermissions = ["gui","user-dirs","sound-card","webcam","access-working-directory","allow-network-access"]
    if areAnyOfThesePermitted(moderatePermissions):
      print(" Moderate permissions(These are probably safe):")
      if not self["gui"] is None:
        print("  Is able to display windows.")
        if self["gui"]["clipboard"]:
          print("  Is able to access the host's clipboard.")
        if self["gui"]["system-tray"]:
          print("  Is able to create system tray icons.")
        if self["gui"]["cursors"]:
          print("  Is able to change the mouse's cursor icon.")
      if not self["user-dirs"]==[]:
        print("  Has access to the following user directories: '~/"+"' '~/".join(self["user-dirs"])+"'")
      if not self["inherit-envvars"]==[]:
        print("  Has access to the following environment variables: "+" ".join(self["inherit-envvars"]))
      if self["sound-card"]:
        print("  Has access to your soundcard, can play sounds/record sound.")
      if self["webcam"]:
        print("  Can access your computer's webcam/can see you.")
      if self["access-working-directory"]:
        print("  Can access the directory from which it was launched.")
      if self["allow-network-access"]:
        print("  Can access the network/internet.")

    liberalPermissions = ["x11","system-dirs","graphics-card","serial-devices","system-dbus","as-root"]
    if areAnyOfThesePermitted(liberalPermissions):
      print(" Liberal permissions(These may pose a security risk):")
      if self["x11"]:
        print("  Can display X11 windows and interact with your X11 server directly(log keypresses, read over your shoulder ect.)")
      if self["system-dirs"]:
        print("  Can read and write the following directories:")
        for source,dest in self["system-dirs"].items():
          print("   "+source+"(mounted as "+dest+")")
      if self["graphics-card"]:
        print(" Can access your graphics-card directly for OpenGL tasks.")
      if self["serial-devices"]:
        print(" Can access serial devices such as programable micro-controlers and modems.")
      if self["system-dbus"]:
        print(" Can talk to the system dbus daemon.")
    anarchisticPermissions = ["privileged"]
    if areAnyOfThesePermitted(anarchisticPermissions):
      print("WARNING: this subuser has full access to your system when run.")
      if self["privileged"]:
        print(" Has full access to your system.  Can even do things as root outside of its container.")

