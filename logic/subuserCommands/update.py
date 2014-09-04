#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

# This command updates all or some of the installed subuser programs.

#external imports
import optparse
#internal imports
import subuserlib.commandLineArguments,subuserlib.classes.user,subuserlib.update


#####################################################################################

def parseCliArgs():
  usage = "usage: subuser %prog [options]"
  description = """Update subuser images.

  all 
      Updates all subuser images which have been marked as out of date.

  EXAMPLE:
    $ subuser update all
 
  log
      Prints a log of recent updates.

  checkout HASH
      Check out an old version of your subuser configuration.
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args()
#################################################################################################

options,args = parseCliArgs()

user = subuserlib.classes.user.User()

if ["all"] == args:
  subuserlib.update.updateAll(user)
elif ["log"] == args:
  subuserlib.update.showLog(user)
elif ["checkout"] == args[0]:
  subuserlib.update.checkout(user,commit=args[1])
else:
  sys.exit(args.join(" ") + " is not a valid update subcommand. Please use subuser update -h for help.")

