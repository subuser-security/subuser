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

def add(user,subuserName,imageSourceIdentifier,permissionsAccepter,prompt=False,forceInternal=False,homeDir=None):
  if subuserName.startswith("!") and not forceInternal:
    sys.exit("A subusers may not have names beginning with ! as these names are reserved for internal use.")
  if subuserName in user.registry.subusers:
    sys.exit("A subuser named "+subuserName+" already exists.")
  user.registry.logChange("Adding subuser "+subuserName+" with image "+imageSourceIdentifier)
  try:
    imageSource = subuserlib.resolve.resolveImageSource(user,imageSourceIdentifier)
  except (KeyError,subuserlib.resolve.ResolutionError) as keyError:
    sys.exit("Could not add subuser.  The image source "+imageSourceIdentifier+" does not exist.\n"+str(keyError))
  addFromImageSource(user,subuserName,imageSource,permissionsAccepter,prompt,homeDir=homeDir)

def addFromImageSource(user,subuserName,imageSource,permissionsAccepter,prompt=False,homeDir=None):
  addFromImageSourceNoVerify(user,subuserName,imageSource,homeDir=homeDir)
  subuser = user.registry.subusers[subuserName]
  subuserlib.verify.verify(user,subusers=[subuser],permissionsAccepter=permissionsAccepter,prompt=prompt)
  user.registry.commit()

def addFromImageSourceNoVerify(user,subuserName,imageSource,homeDir=None):
  subuser = subuserlib.classes.subuser.Subuser(user,subuserName,None,False,False,[],imageSource=imageSource,nonDefaultHomeDir=homeDir)
  user.registry.subusers[subuserName] = subuser

def remove(user,subusers):
  didSomething = False
  for subuser in subusers:
    user.registry.logChange("Removing subuser "+str(subuser.name))
    try:
      subuserHome = subuser.homeDirOnHost
      if subuserHome and os.path.exists(subuserHome):
        user.registry.logChange(" If you wish to remove the subusers home directory, issule the command $ rm -r "+subuserHome)
    except:
      pass
    user.registry.logChange(" If you wish to remove the subusers image, issue the command $ subuser remove-old-images")
    for serviceSubuserName in subuser.serviceSubuserNames:
      try:
        serviceSubuser = user.registry.subusers[serviceSubuserName]
        serviceSubuser.removePermissions()
        del user.registry.subusers[serviceSubuserName]
      except KeyError:
        pass
    # Remove service locks
    try:
      shutil.rmtree(os.path.join(user.config["lock-dir"],"services",subuser.name))
    except OSError:
      pass
    # Remove permission files
    subuser.removePermissions()
    del user.registry.subusers[subuser.name]
    didSomething = True
  if didSomething:
    subuserlib.verify.verify(user)
    user.registry.commit()

def changeImage(user,subuserName,imageSourceIdentifier,permissionsAccepter,prompt=False):
  if not subuserName in user.registry.subusers:
    sys.exit("Subuser "+subuserName+" does not exist.")
  user.registry.logChange("Changing the image for subuser "+subuserName+" to "+imageSourceIdentifier)
  try:
    imageSource = subuserlib.resolve.resolveImageSource(user,imageSourceIdentifier)
  except (KeyError,subuserlib.resolve.ResolutionError) as keyError:
    sys.exit("Could not change image.  The image source "+imageSourceIdentifier+" does not exist.\n"+str(keyError))
  subuser = user.registry.subusers[subuserName]
  subuser.imageSource = imageSource
  subuserlib.verify.verify(user,subusers=[subuser],permissionsAccepter=permissionsAccepter,prompt=prompt)
  user.registry.commit()

def setExecutableShortcutInstalled(user,subusers,installed):
  for subuser in subusers:
    if installed:
      user.registry.logChange("Adding launcher for subuser "+subuser.name+" to $PATH.")
    else:
      user.registry.logChange("Removing launcher for subuser "+subuser.name+" from $PATH.")
    subuser.executableShortcutInstalled = installed
  subuserlib.verify.verify(user)
  user.registry.commit()

def setEntrypointsExposed(user,subusers,exposed,permissionsAccepter):
  for subuser in subusers:
    if exposed:
      user.registry.logChange("Exposing entrypoints for subuser "+subuser.name+" in the $PATH.")
    else:
      user.registry.logChange("Removing entrypoints for subuser "+subuser.name+" from $PATH.")
    subuser.entrypointsExposed = exposed
  subuserlib.verify.verify(user,subusers=subusers,permissionsAccepter=permissionsAccepter)
  user.registry.commit()
