#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

# This command updates all or some of the installed subuser images.

#external imports
import optparse,sys
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

  lock-subuser-to HASH
      Don't want a subuser to be updated?  No problem, lock it to a given version with this update sub-command.  Use subuser update log to see a list of possible hashes.

  rollback HASH
      Subuser's undo function.  Roll back to an old version of your subuser configuration.  Find the commit hash using subuser update log.  Note: This command is less usefull than lock-subuser-to.
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
  >>> set([i.getImageSourceName() for i in user.getInstalledImages().values()]) == set([u'foo', u'bar'])
  True
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
  >>> subuserNamesBeforeUpdate = user.getRegistry().getSubusers().keys()
  >>> set(subuserNamesBeforeUpdate) == set(['dependent', u'foo'])
  True
  >>> installedImagesBeforeUpdate = [i.getImageSourceName() for i in user.getInstalledImages().values()]
  >>> set(installedImagesBeforeUpdate) == set([u'foo', u'dependency1', u'bar', u'dependent', u'intermediary'])
  True

  Running update, when there is nothing to be updated, does nothing.

  >>> update.update(user,["update","all"])
  Updating...
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Running garbage collector on temporary repositories...
  >>> set(user.getRegistry().getSubusers().keys()) == set(subuserNamesBeforeUpdate)
  True
  >>> set([i.getImageSourceName() for i in user.getInstalledImages().values()]) == set(installedImagesBeforeUpdate)
  True
  >>> with open(user.getRegistry().getRepositories()[u'remote-repo']["intermediary"].getSubuserImagefilePath(),mode="w") as subuserImagefile:
  ...   subuserImagefile.write("FROM-SUBUSER-IMAGE dependency2")
  >>> subuserlib.git.runGit(["commit","-a","-m","changed dependency for intermediate from dependency1 to dependency2"],cwd=user.getRegistry().getRepositories()[u'remote-repo'].getRepoPath())

  Running an update after a change installs new images and registers them with their subusers.  But it does not delete the old ones.

  >>> update.update(user,["update","all"])
  Updating...
  Updated repository remote-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Installing dependency2 ...
  Installing intermediary ...
  Installing dependent ...
  Installed new image for subuser dependent
  Running garbage collector on temporary repositories...
  >>> set(user.getRegistry().getSubusers().keys()) == set(['dependent', u'foo'])
  True
  >>> set([i.getImageSourceName() for i in user.getInstalledImages().values()]) == set([u'foo', u'dependency1', u'bar', u'dependent', u'intermediary', u'intermediary', u'dependency2', u'dependent'])
  True

  Old images are not deleted so that update lock-subuser-to and update rollback still work. In this example, dependency1 stays installed.
  """
  options,args = parseCliArgs(sysargs)
  if len(args) < 1:
    sys.exit("No arguments given. Please use subuser update -h for help.")
  elif ["all"] == args:
    subuserlib.update.updateAll(user)
  elif ["log"] == args:
    subuserlib.update.showLog(user)
  elif len(args) == 1:
    sys.exit(" ".join(args) + " is not a valid update subcommand. Please use subuser update -h for help.")
  elif "rollback" == args[0]:
    subuserlib.update.rollback(user,commit=args[1])
  else:
    sys.exit(" ".join(args) + " is not a valid update subcommand. Please use subuser update -h for help.")

if __name__ == "__main__":
  user = subuserlib.classes.user.User()
  update(user,sys.argv)
