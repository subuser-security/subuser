# -*- coding: utf-8 -*-

"""
High level operations on subusers.
"""

#external imports
import sys
import os
import shutil
#internal imports
import subuserlib.resolve
import subuserlib.classes.subuser
import subuserlib.verify
import subuserlib.update
import subuserlib.classes.exceptions as exceptions

def add(user,subuserName,imageSourceIdentifier,homeDir=None):
  if subuserName in user.registry.subusers:
    sys.exit("A subuser named "+subuserName+" already exists.")
  user.registry.logChange("Adding subuser "+subuserName+" with image "+imageSourceIdentifier)
  try:
    imageSource = subuserlib.resolve.resolveImageSource(user,imageSourceIdentifier)
  except (subuserlib.resolve.ResolutionError) as keyError:
    sys.exit("Could not add subuser.  The image source "+imageSourceIdentifier+" does not exist.\n"+str(keyError))
  addFromImageSource(user,subuserName,imageSource,homeDir=homeDir)

def addFromImageSource(user,subuserName,imageSource,homeDir=None):
  addFromImageSourceNoVerify(user,subuserName,imageSource,homeDir=homeDir)
  user.operation.subusers.append(user.registry.subusers[subuserName])
  subuserlib.verify.verify(user.operation)
  user.registry.commit()

def addFromImageSourceNoVerify(user,subuserName,imageSource,homeDir=None):
  subuser = subuserlib.classes.subuser.Subuser(user,subuserName,None,False,False,[],imageSource=imageSource,nonDefaultHomeDir=homeDir)
  user.registry.subusers[subuserName] = subuser

def remove(operation):
  didSomething = False
  registry = operation.user.registry
  for subuser in operation.subusers:
    registry.logChange("Removing subuser "+str(subuser.name))
    try:
      subuserHome = subuser.homeDirOnHost
      if subuserHome and os.path.exists(subuserHome):
        registry.logChange(" If you wish to remove the subusers home directory, issue the command $ rm -r "+subuserHome)
    except:
      pass
    registry.logChange(" If you wish to remove the subusers image, issue the command $ subuser remove-old-images")
    for serviceSubuserName in subuser.serviceSubuserNames:
      try:
        serviceSubuser = registry.subusers[serviceSubuserName]
        serviceSubuser.removePermissions()
        del registry.subusers[serviceSubuserName]
      except KeyError:
        pass
    # Remove service locks
    try:
      shutil.rmtree(os.path.join(operation.user.config["lock-dir"],"services",subuser.name))
    except OSError:
      pass
    # Remove permission files
    subuser.removePermissions()
    del registry.subusers[subuser.name]
    didSomething = True
  if didSomething:
    operation.subusers = []
    subuserlib.verify.verify(operation)
    registry.commit()

def changeImage(user,imageSourceIdentifier):
  subuser = user.operation.subusers[0]
  user.registry.logChange("Changing the image for subuser "+subuser.name+" to "+imageSourceIdentifier)
  try:
    imageSource = subuserlib.resolve.resolveImageSource(user,imageSourceIdentifier)
  except (subuserlib.resolve.ResolutionError) as e:
    sys.exit("Could not change image.  The image source "+imageSourceIdentifier+" does not exist.\n"+str(e))
  subuser.imageSource = imageSource
  subuserlib.verify.verify(user.operation)
  user.registry.commit()

def setExecutableShortcutInstalled(operation,installed):
  registry = operation.user.registry
  for subuser in operation.subusers:
    if installed:
      registry.logChange("Adding launcher for subuser "+subuser.name+" to $PATH.")
    else:
      registry.logChange("Removing launcher for subuser "+subuser.name+" from $PATH.")
    subuser.executableShortcutInstalled = installed
  subuserlib.verify.verify(operation)
  registry.commit()

def setEntrypointsExposed(operation,exposed):
  registry = operation.user.registry
  for subuser in operation.subusers:
    if exposed:
      registry.logChange("Exposing entrypoints for subuser "+subuser.name+" in the $PATH.")
    else:
      registry.logChange("Removing entrypoints for subuser "+subuser.name+" from $PATH.")
    subuser.entrypointsExposed = exposed
  subuserlib.verify.verify(operation)
  registry.commit()
