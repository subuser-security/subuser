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
from subuserlib.classes.user import User
import subuserlib.profile

##############################################################
helpString = """Run the given subuser.

For example:

    $ subuser run iceweasel

Will launch the subuser named iceweasel

If the SUBUSER_EXTRA_DOCKER_ARGS environment variable is set. Those arguments will be passed to Docker.
"""

#################################################################################################

@subuserlib.profile.do_cprofile
def run(args):
  if len(args) == 1 or args[1] == "-h" or args[1] == "--help":
    print(helpString)
    sys.exit()

  subuserName = args[1]
  argsToPassToImage = args[2:]

  user = User()
  user.getRegistry().setLogOutputVerbosity(0)
  if subuserName in user.getRegistry().getSubusers():
    try:
      extraDockerFlags = os.environ["SUBUSER_EXTRA_DOCKER_ARGS"].split(" ")
    except KeyError:
      extraDockerFlags = []
    runtime = user.getRegistry().getSubusers()[subuserName].getRuntime(os.environ,extraDockerFlags=extraDockerFlags)
    if runtime:
      runtime.run(argsToPassToImage)
    else:
      sys.exit("The subuser's image failed to build. Please use the subuser registry log and subuser repair commands for more information.")
  else:
    sys.exit(subuserName + " not found.\n"+helpString)

run(sys.argv)
