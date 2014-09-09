#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

# This command updates all or some of the installed subuser images.

#external imports
import optparse
#internal imports
import subuserlib.commandLineArguments,subuserlib.classes.user,subuserlib.update


#####################################################################################

def parseCliArgs(sysargs):
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
  return parser.parse_args(sysargs[1:])
#################################################################################################

def update(user,sysargs):
  """
  >>> import update #import self
  >>> import subuser
  >>> import os
  >>> import subuserlib.git
  >>> user = subuserlib.classes.user.User()
  >>> user.getRegistry().getSubusers().keys()
  [u'foo']
  >>> [i.getImageSourceName() for i in user.getInstalledImages().values()]
  [u'foo', u'bar']
  >>> subuser.subuser(user,["subuser","add","dependent","dependent@file:///home/travis/remote-test-repo"])
  Adding subuser dependent dependent@file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Installing dependency1 ...
  Installing intermediary ...
  Installing dependent ...
  Installed new image for subuser dependent
  Running garbage collector on temporary repositories...
  >>> user.getRegistry().getSubusers().keys()
  ['dependent', u'foo']
  >>> [i.getImageSourceName() for i in user.getInstalledImages().values()]
  [u'foo', u'dependency1', u'bar', u'dependent', u'intermediary']
  >>> update.update(user,["update","all"])
  Updating...
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Running garbage collector on temporary repositories...
  >>> user.getRegistry().getSubusers().keys()
  ['dependent', u'foo']
  >>> [i.getImageSourceName() for i in user.getInstalledImages().values()]
  [u'foo', u'dependency1', u'bar', u'dependent', u'intermediary']
  >>> with open(user.getRegistry().getRepositories()[u'remote-repo']["intermediary"].getSubuserImagefilePath(),mode="w") as subuserImagefile:
  ...   subuserImagefile.write("FROM-SUBUSER-IMAGE dependency2")
  >>> subuserlib.git.runGit(["commit","-a","-m","changed dependency for intermediate from dependency1 to dependency2"],cwd=user.getRegistry().getRepositories()[u'remote-repo'].getRepoPath())
  >>> update.update(user,["update","all"])
  Updating...
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Installing dependency2 ...
  Installing intermediary ...
  Installing dependent ...
  Installed new image for subuser dependent
  Running garbage collector on temporary repositories...
  >>> user.getRegistry().getSubusers().keys()
  ['dependent', u'foo']
  >>> [i.getImageSourceName() for i in user.getInstalledImages().values()]
  [u'foo', u'dependency1', u'bar', u'dependent', u'intermediary', u'intermediary', u'dependency2', u'dependent']

  Note that dependency1 stays installed, so we can always use subuser update checkout to go back to the version before the update.
  """
  options,args = parseCliArgs(sysargs)
  if ["all"] == args:
    subuserlib.update.updateAll(user)
  elif ["log"] == args:
    subuserlib.update.showLog(user)
  elif ["checkout"] == args[0]:
    subuserlib.update.checkout(user,commit=args[1])
  else:
    sys.exit(args.join(" ") + " is not a valid update subcommand. Please use subuser update -h for help.")

if __name__ == "__main__":
  user = subuserlib.classes.user.User()
  update(user,sys.argv)
