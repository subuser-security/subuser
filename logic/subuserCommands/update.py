#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

# This command updates all or some of the installed subuser images.

import pathConfig
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

  lock-subuser-to SUBUSER GIT-COMMIT
      Don't want a subuser to be updated?  No problem, lock it to a given version with this update sub-command.  Use subuser update log to see a list of possible hashes.

  unlock-subuser SUBUSER
      Unlock the subuser and ensure that it is up-to-date.

  rollback HASH
      Subuser's undo function.  Roll back to an old version of your subuser configuration.  Find the commit hash using subuser update log.  Note: This command is less usefull than lock-subuser-to.
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args(sysargs)

#################################################################################################

def update(user,sysargs):
  """
  Update your subuser installation.

  Tests
  -----

  **Setup:**

  >>> import os
  >>> import update,subuser,subuserlib.git
  >>> user = subuserlib.classes.user.User()

  Check initial test environment:

  >>> set(user.getRegistry().getSubusers().keys()) == set([u'foo'])
  True
  >>> set([i.getImageSourceName() for i in user.getInstalledImages().values()]) == set([u'foo', u'bar'])
  True

  Add a subuser who's image has a lot of dependencies.

  >>> subuser.subuser(user,["add","dependent","dependent@file:///home/travis/remote-test-repo"])
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

  Check that our new subuser was successfully added.

  >>> subuserNamesBeforeUpdate = user.getRegistry().getSubusers().keys()
  >>> set(subuserNamesBeforeUpdate) == set(['dependent', u'foo'])
  True

  And that its image, along with all of its dependencies were added as well.

  >>> installedImagesBeforeUpdate = [i.getImageSourceName() for i in user.getInstalledImages().values()]
  >>> set(installedImagesBeforeUpdate) == set([u'foo', u'dependency1', u'bar', u'dependent', u'intermediary'])
  True

  Running update, when there is nothing to be updated, does nothing.

  >>> update.update(user,["all"])
  Updating...
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Running garbage collector on temporary repositories...

  The same subusers are still installed.

  >>> set(user.getRegistry().getSubusers().keys()) == set(subuserNamesBeforeUpdate)
  True

  And the same images too.

  >>> set([i.getImageSourceName() for i in user.getInstalledImages().values()]) == set(installedImagesBeforeUpdate)
  True

  Now we change the ImageSource for the ``dependent`` image.

  >>> with open(user.getRegistry().getRepositories()[u'remote-repo']["intermediary"].getSubuserImagefilePath(),mode="w") as subuserImagefile:
  ...   _ = subuserImagefile.write("FROM-SUBUSER-IMAGE dependency2")

  And commit the changes to git.

  >>> subuserlib.git.runGit(["commit","-a","-m","changed dependency for intermediate from dependency1 to dependency2"],cwd=user.getRegistry().getRepositories()[u'remote-repo'].getRepoPath())

  Running an update after a change installs new images and registers them with their subusers.  But it does not delete the old ones.

  >>> update.update(user,["all"])
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

  Now we lock the dependent subuser and try changing it again.

  >>> update.update(user,["lock-subuser-to","dependent","HEAD"])
  Locking subuser dependent to commit: HEAD
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Running garbage collector on temporary repositories...

  >>> with open(user.getRegistry().getRepositories()[u'remote-repo']["intermediary"].getSubuserImagefilePath(),mode="w") as subuserImagefile:
  ...   _ = subuserImagefile.write("FROM-SUBUSER-IMAGE dependency3")

  And commit the changes to git.

  >>> subuserlib.git.runGit(["commit","-a","-m","changed dependency for intermediate from dependency2 to dependency3"],cwd=user.getRegistry().getRepositories()[u'remote-repo'].getRepoPath())

  Running an update after a change does nothing because the affected subuser is locked.

  >>> update.update(user,["all"])
  Updating...
  Updated repository remote-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Running garbage collector on temporary repositories...

  >>> set(user.getRegistry().getSubusers().keys()) == set(['dependent', u'foo'])
  True

  >>> set([i.getImageSourceName() for i in user.getInstalledImages().values()]) == set([u'foo', u'dependency1', u'bar', u'dependent', u'intermediary', u'intermediary', u'dependency2', u'dependent'])
  True

  When we unlock the subuser it gets updated imediately.

  >>> update.update(user,["unlock-subuser","dependent"])
  Unlocking subuser dependent
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Installing dependency3 ...
  Installing intermediary ...
  Installing dependent ...
  Installed new image for subuser dependent
  Running garbage collector on temporary repositories...

  >>> set(user.getRegistry().getSubusers().keys()) == set(['dependent', u'foo'])
  True

  >>> set([i.getImageSourceName() for i in user.getInstalledImages().values()]) == set([u'foo', u'dependency1', u'bar', u'dependent', u'intermediary', u'intermediary', u'dependency2',u'dependency3', u'dependent'])
  True
  """
  options,args = parseCliArgs(sysargs)
  if len(args) < 1:
    sys.exit("No arguments given. Please use subuser update -h for help.")
  elif ["all"] == args:
    subuserlib.update.updateAll(user)
  elif ["log"] == args:
    subuserlib.update.showLog(user)
  elif "lock-subuser-to" == args[0]:
    try:
      subuserName = args[1]
      commit = args[2]
    except KeyError:
      sys.exit("Wrong number of arguments.  Expected a subuser name and a commit.  Try running\nsubuser update --help\n for more info.")
    subuserlib.update.lockSubuser(user,subuserName=subuserName,commit=commit)
  elif "unlock-subuser" == args[0]:
    try:
      subuserName = args[1]
    except KeyError:
      sys.exit("Wrong number of arguments.  Expected a subuser's name. Try running\nsubuser update --help\nfor more information.")
    subuserlib.update.unlockSubuser(user,subuserName=subuserName)
  elif "rollback" == args[0]:
    try:
      commit = args[1]
    except KeyError:
      sys.exit("Wrong number of arguments.  Expected a commit.  Try running \nsubuser update --help\nfor more info.")
    subuserlib.update.rollback(user,commit=commit)
  elif len(args) == 1:
    sys.exit(" ".join(args) + " is not a valid update subcommand. Please use subuser update -h for help.")
  else:
    sys.exit(" ".join(args) + " is not a valid update subcommand. Please use subuser update -h for help.")

if __name__ == "__main__":
  user = subuserlib.classes.user.User()
  update(user,sys.argv)

