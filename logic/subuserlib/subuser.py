#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
High level operations on subusers.
"""

#external imports
import sys
#internal imports
import subuserlib.classes.user,subuserlib.resolve,subuserlib.classes.subuser,subuserlib.verify,subuserlib.update

def add(user,subuserName,imageSourceIdentifier):
  if subuserName in user.getRegistry().getSubusers():
    sys.exit("A subuser named "+subuserName+" already exists.")
  user.getRegistry().logChange("Adding subuser "+subuserName+" "+imageSourceIdentifier)
  try:
    try:
      imageSource = subuserlib.resolve.resolveImageSource(user,imageSourceIdentifier)
    except KeyError as keyError:
      sys.exit("Could not add subuser.  The image source "+imageSourceIdentifier+" does not exist.")
    user.getRegistry().getSubusers()[subuserName] = subuserlib.classes.subuser.Subuser(user,subuserName,imageSource,None,False,False)
    subuserlib.verify.verify(user)
    user.getRegistry().commit()
  except subuserlib.classes.dockerDaemon.ImageBuildException as e:
    print("Adding subuser failed.")
    print(str(e))
    subuserlib.update.checkoutNoCommit(user,"HEAD")

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
