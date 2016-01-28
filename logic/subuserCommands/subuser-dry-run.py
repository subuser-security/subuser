#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
  import pathConfig
except ImportError:
  pass
#external imports
import sys
import os
#internal imports
import subuserlib.classes.user
import subuserlib.profile

##############################################################
helpString = """
Display the command which would be issued to launch Docker if you were to run this subuser.

For example:

    $ subuser dry-run iceweasel

Will display the command used to launch the subuser iceweasel.

Please note, this is only a rough approximation for debugging purposes and there is no guarantee that the command displayed here would actually work.
"""

#################################################################################################
def dryRunTestSetup():
  import sys,os,getpass
  os.getuid = lambda: 1000
  getpass.getuser = lambda: "travis"

@subuserlib.profile.do_cprofile
def dryRun(args):
  if len(args) == 0 or {"help","-h","--help"} & set(args):
    print(helpString)
    sys.exit()
  subuserName = args[0]
  argsToPassToImage = args[1:]
  user = subuserlib.classes.user.User()
  if subuserName in user.getRegistry().getSubusers():
    subuser = user.getRegistry().getSubusers()[subuserName]
    if subuser.getImageId():
      print("The image will be prepared using the Dockerfile:")
      print(subuser.getRunReadyImage().generateImagePreparationDockerfile())
      print("The command to launch the image is:")
      print(subuser.getRuntime(os.environ).getPrettyCommand(argsToPassToImage))
    else:
      print("The subuser "+subuserName+" has no installed image and therefore cannot be run.")
  else:
    availableSubusers = ",".join(user.getRegistry().getSubusers().keys())
    sys.exit(subuserName + " not found.\n"+helpString+"\n"+"The following subusers are available for use:"+ availableSubusers)

if __name__ == "__main__":
  dryRun(sys.argv[1:])
