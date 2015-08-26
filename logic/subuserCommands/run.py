#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import pathConfig
#external imports
import sys
import os
import cProfile
#internal imports
from subuserlib.classes.user import User

##############################################################
helpString = """Run the given subuser.

For example:

    $ subuser run iceweasel

Will launch the subuser named iceweasel
"""

#################################################################################################

def do_cprofile(func):
    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats(sort='cumtime')
    return profiled_func

#@do_cprofile
def run(args):
  if len(args) == 1 or args[1] == "-h" or args[1] == "--help":
    print(helpString)
    sys.exit()

  subuserName = args[1]
  argsToPassToImage = args[2:]

  user = User()
  user.getRegistry().setLogOutputVerbosity(0)
  if subuserName in user.getRegistry().getSubusers():
    runtime = user.getRegistry().getSubusers()[subuserName].getRuntime(os.environ)
    if runtime:
      runtime.run(argsToPassToImage)
    else:
      sys.exit("The subuser's image failed to build. Please use the subuser update log and subuser repair commands for more information.")
  else:
    sys.exit(subuserName + " not found.\n"+helpString)

run(sys.argv)
