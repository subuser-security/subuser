#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

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
import subuserlib.classes.docker.dockerDaemon as dockerDaemon

def add(user,subuserName,imageSourceIdentifier):
  if subuserName.startswith("!"):
    sys.exit("A subusers may not have names beginning with ! as these names are reserved for internal use.")
  if subuserName in user.getRegistry().getSubusers():
    sys.exit("A subuser named "+subuserName+" already exists.")
  user.getRegistry().logChange("Adding subuser "+subuserName+" "+imageSourceIdentifier)
  try:
    imageSource = subuserlib.resolve.resolveImageSource(user,imageSourceIdentifier)
  except KeyError as keyError:
    sys.exit("Could not add subuser.  The image source "+imageSourceIdentifier+" does not exist.")
  addFromImageSource(user,subuserName,imageSource)

def addFromImageSource(user,subuserName,imageSource):
  try:
    addFromImageSourceNoVerify(user,subuserName,imageSource)
    subuserlib.verify.verify(user,subuserNames=[subuserName])
    user.getRegistry().commit()
  except dockerDaemon.ImageBuildException as e:
    print("Adding subuser failed.")
    print(str(e))
    subuserlib.update.checkoutNoCommit(user,"HEAD")

def addFromImageSourceNoVerify(user,subuserName,imageSource):
    subuser = subuserlib.classes.subuser.Subuser(user,subuserName,imageSource,None,False,False,[])
    if not subuser.getPermissions()["gui"] is None:
      subuser.getX11Bridge().setup(verify=False)
    user.getRegistry().getSubusers()[subuserName] = subuser

def remove(user,subuserNames):
  didSomething = False
  for subuserName in subuserNames:
    if subuserName in user.getRegistry().getSubusers():
      user.getRegistry().logChange("Removing subuser "+str(subuserName))
      try:
        subuserHome = user.getRegistry().getSubusers()[subuserName].getHomeDirOnHost()
        if subuserHome:
          user.getRegistry().logChange(" If you wish to remove the subusers home directory, issule the command $ rm -r "+subuserHome)
      except:
        pass
      user.getRegistry().logChange(" If you wish to remove the subusers image, issue the command $ subuser remove-old-images")
      subuser = user.getRegistry().getSubusers()[subuserName]
      for serviceSubuser in subuser.getServiceSubuserNames():
        try:
          del user.getRegistry().getSubusers()[serviceSubuser]
        except KeyError:
          pass
      # Remove service locks
      try:
        shutil.rmtree(os.path.join(user.getConfig()["lock-dir"],"services",subuserName))
      except OSError:
        pass
      del user.getRegistry().getSubusers()[subuserName]
      didSomething = True
    else:
      print("Cannot remove: subuser "+subuserName+" does not exist.")
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
