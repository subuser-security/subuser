#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import json,os,sys,collections
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
    if not self["user-dirs"]==[]:
      print(" Has access to the following user directories: '~/"+"' '~/".join(self["user-dirs"])+"'")
    if not self["system-dirs"]==[]:
      print(" Can read from the following system directories: '"+"' '".join(self["system-dirs"])+"'")
    if self["x11"]:
      print(" Can display X11 windows.")
    if self["graphics-card"]:
      print(" Can access your graphics-card directly for OpenGL tasks.")
    if self["sound-card"]:
      print(" Has access to your soundcard, can play sounds/record sound.")
    if self["webcam"]:
      print(" Can access your computer's webcam/can see you.")
    if self["inherit-working-directory"]:
      print(" Can access the directory from which it was launched.")
    if self["allow-network-access"]:
      print(" Can access the network/internet.")
    if self["privileged"]:
      print(" Is fully privileged.  NOTE: Highly insecure!")
