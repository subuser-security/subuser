#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import sys
#internal imports
import subuserlib.classes.user, subuserlib.run

##############################################################
helpString = """Run the given subuser program.  For example:
$ subuser run firefox

Will launch firefox.
"""

#################################################################################################

def run(args):
  if len(args) == 1 or {"help","-h","--help"} & set(args):
    sys.exit(helpString)

  subuserName = args[1]
  argsToPassToProgram = args[2:]

  user = subuserlib.classes.user.User()
  if subuserName in user.getRegistry().getSubusers():
    subuserlib.run.run(user.getRegistry().getSubusers()[subuserName],argsToPassToProgram))
  else:
    sys.exit(subuserName + " not found.\n"+helpString)

run(sys.argv)
