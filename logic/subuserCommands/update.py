#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

# This command updates all or some of the installed subuser programs.

#external imports
#import ...
#internal imports
import subuserlib.commandLineArguments,subuserlib.classes.user,subuserlib.verify,subuserlib.git


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
  user.getRegistry().log("Updating...")
  for _,repository in user.getRegistry().getRepositories().iteritems():
    repository.updateSources()
  subuserlib.verify.verify(user)
  user.getRegistry().commit()
elif ["log"] == args:
  subuserlib.git.runGit(["log"],cwd=user.getConfig().getRegistryPath())
elif ["checkout"] == args[0]:
  user.getRegistry().logChange("Rolling back to commit: "+args[1])
  subuserlib.git.runGit(["rm","-r","."],cwd=user.getConfig().getRegistryPath())
  subuserlib.git.runGit(["checkout",args[1]],cwd=user.getConfig().getRegistryPath())
  user.getRegistry().getRepositories().reloadRepositoryLists()
  subuserlib.verify.verify(user)
  user.getRegistry().commit()
else:
  sys.exit(args.join(" ") + " is not a valid update subcommand. Please use subuser update -h for help.")

