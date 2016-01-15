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

def add(user,subuserName,imageSourceIdentifier,permissionsAccepter,prompt=False,forceInternal=False):
  if subuserName.startswith("!") and not forceInternal:
    sys.exit("A subusers may not have names beginning with ! as these names are reserved for internal use.")
  if subuserName in user.getRegistry().getSubusers():
    sys.exit("A subuser named "+subuserName+" already exists.")
  user.getRegistry().logChange("Adding subuser "+subuserName+" with image "+imageSourceIdentifier)
  try:
    imageSource = subuserlib.resolve.resolveImageSource(user,imageSourceIdentifier)
  except KeyError as keyError:
    sys.exit("Could not add subuser.  The image source "+imageSourceIdentifier+" does not exist.\n"+str(keyError))
  addFromImageSource(user,subuserName,imageSource,permissionsAccepter,prompt)

def addFromImageSource(user,subuserName,imageSource,permissionsAccepter,prompt=False):
  addFromImageSourceNoVerify(user,subuserName,imageSource)
  subuser = user.getRegistry().getSubusers()[subuserName]
  subuserlib.verify.verify(user,subusers=[subuser],permissionsAccepter=permissionsAccepter,prompt=prompt)
  user.getRegistry().commit()

def addFromImageSourceNoVerify(user,subuserName,imageSource):
  subuser = subuserlib.classes.subuser.Subuser(user,subuserName,None,False,False,[],imageSource=imageSource)
  user.getRegistry().getSubusers()[subuserName] = subuser

def remove(user,subusers):
  didSomething = False
  for subuser in subusers:
    user.getRegistry().logChange("Removing subuser "+str(subuser.getName()))
    try:
      subuserHome = subuser.getHomeDirOnHost()
      if subuserHome and os.path.exists(subuserHome):
        user.getRegistry().logChange(" If you wish to remove the subusers home directory, issule the command $ rm -r "+subuserHome)
    except:
      pass
    user.getRegistry().logChange(" If you wish to remove the subusers image, issue the command $ subuser remove-old-images")
    for serviceSubuserName in subuser.getServiceSubuserNames():
      try:
        serviceSubuser = user.getRegistry().getSubusers()[serviceSubuser]
        serviceSubuser.removePermissions()
        del user.getRegistry().getSubusers()[serviceSubuserName]
      except KeyError:
        pass
    # Remove service locks
    try:
      shutil.rmtree(os.path.join(user.getConfig()["lock-dir"],"services",subuser.getName()))
    except OSError:
      pass
    # Remove permission files
    subuser.removePermissions()
    del user.getRegistry().getSubusers()[subuser.getName()]
    didSomething = True
  if didSomething:
    subuserlib.verify.verify(user)
    user.getRegistry().commit()

def setExecutableShortcutInstalled(user,subuserName,installed):
  if installed:
    user.getRegistry().logChange("Creating shortcut for subuser "+subuserName)
  else:
    user.getRegistry().logChange("Removing shortcut for subuser "+subuserName)
  user.getRegistry().getSubusers()[subuserName].setExecutableShortcutInstalled(installed)
  subuserlib.verify.verify(user)
  user.getRegistry().commit()
