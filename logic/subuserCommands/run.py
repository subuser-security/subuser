#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import sys
#internal imports
import subuserlib.classes.user, subuserlib.run

##############################################################
helpString = """Run the given subuser.

For example:

    $ subuser run firefox

Will launch the subuser named firefox.
"""

#################################################################################################

def run(args):
  if len(args) == 1 or args[1] == "--help":
    print(helpString)
    sys.exit()

  subuserName = args[1]
  argsToPassToImage = args[2:]

  user = subuserlib.classes.user.User()
  if subuserName in user.getRegistry().getSubusers():
    subuserlib.run.run(user.getRegistry().getSubusers()[subuserName],argsToPassToImage)
  else:
    sys.exit(subuserName + " not found.\n"+helpString)

run(sys.argv)
