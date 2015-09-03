#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

# This command updates all or some of the installed subuser images.

import pathConfig
#external imports
import sys
import optparse
#internal imports
import subuserlib.commandLineArguments
from subuserlib.classes.user import User
import subuserlib.update
import subuserlib.profile
from subuserlib.classes.permissionsAccepters.acceptPermissionsAtCLI import AcceptPermissionsAtCLI

#####################################################################################

def parseCliArgs(realArgs):
  usage = "usage: subuser %prog [options]"
  description = """Update subuser images.

  all 
      Updates all subuser images which have been marked as out of date.

  EXAMPLE:
    $ subuser update all

  subusers
      Updates the specified subusers

  EXAMPLE:
    $ subuser update subuser iceweasel git
 
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
  parser.add_option("--accept",dest="accept",action="store_true",default=False,help="Accept permissions without asking.")
  return parser.parse_args(args=realArgs)

#################################################################################################

@subuserlib.profile.do_cprofile
def update(realArgs):
  """
  Update your subuser installation.

  Tests
  -----

  **Setup:**

  >>> import os
  >>> import update,subuser,subuserlib.classes.gitRepository,repository

  Check initial test environment:

  >>> user = User()
  >>> set(user.getRegistry().getSubusers().keys()) == set([u'foo'])
  True
  >>> set([i.getImageSourceName() for i in user.getInstalledImages().values()]) == set([u'foo', u'bar'])
  True

  Add a subuser who's image has a lot of dependencies.

  >>> subuser.subuser(["add","--accept","dependent","dependent@file:///home/travis/remote-test-repo"])
  Adding subuser dependent dependent@file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  dependent would like to have the following permissions:
   Description: a dependent
   Maintainer: 
   Is a library.
   Moderate permissions(These are probably safe):
    - user-dirs: To access to the following user directories: '~/Downloads'
    - sound-card: To access to your soundcard, can play sounds/record sound.
   Liberal permissions(These may pose a security risk):
    - x11: To display X11 windows and interact with your X11 server directly(log keypresses, read over your shoulder, steal your passwords, controll your computer ect.)
    - system-dirs: To read and write to the host's `/var/log` directory, mounted in the container as:`/var/log`
   WARNING: These permissions give the subuser full access to your system when run.
    - privileged: To have full access to your system.  To even do things as root outside of its container.
  A - Accept and apply changes
  E - Apply changes and edit result
  A
  Checking if images need to be updated or installed...
  Checking if subuser dependent is up to date.
  Installing dependency1 ...
  Building...
  Building...
  Building...
  Successfully built 13
  Building...
  Building...
  Building...
  Successfully built 14
  Installing intermediary ...
  Building...
  Building...
  Building...
  Successfully built 15
  Building...
  Building...
  Building...
  Successfully built 16
  Installing dependent ...
  Building...
  Building...
  Building...
  Successfully built 17
  Building...
  Building...
  Building...
  Successfully built 18
  Installed new image <18> for subuser dependent
  Running garbage collector on temporary repositories...

  Check that our new subuser was successfully added.

  >>> user = User()
  >>> subuserNamesBeforeUpdate = user.getRegistry().getSubusers().keys()
  >>> set(subuserNamesBeforeUpdate) == set(['dependent', u'foo'])
  True

  And that its image, along with all of its dependencies were added as well.

  >>> installedImagesBeforeUpdate = [i.getImageSourceName() for i in user.getInstalledImages().values()]
  >>> set(installedImagesBeforeUpdate) == set([u'foo', u'dependency1', u'bar', u'dependent', u'intermediary'])
  True

  Running update, when there is nothing to be updated, does nothing.

  >>> update.update(["all","--accept"])
  Updating...
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Checking if subuser dependent is up to date.
  Checking for updates to: dependency1@file:///home/travis/remote-test-repo
  Checking for updates to: intermediary@file:///home/travis/remote-test-repo
  Checking for updates to: dependent@file:///home/travis/remote-test-repo
  Checking if subuser foo is up to date.
  Checking for updates to: foo@default
  Running garbage collector on temporary repositories...

  The same subusers are still installed.

  >>> user = User()
  >>> set(user.getRegistry().getSubusers().keys()) == set(subuserNamesBeforeUpdate)
  True

  And the same images too.

  >>> set([i.getImageSourceName() for i in user.getInstalledImages().values()]) == set(installedImagesBeforeUpdate)
  True

  However, if we change ``dependent``'s image source's permissions, the user is asked to approve the new permissions:

  >>> permissions = user.getRegistry().getRepositories()[u'1']["dependent"].getPermissions()
  >>> del permissions["sound-card"]
  >>> permissions["user-dirs"] = ["Images","Downloads"]
  >>> permissions.save()

  >>> repo1 = subuserlib.classes.gitRepository.GitRepository(user.getRegistry().getRepositories()[u'1'].getRepoPath())
  >>> repo1.run(["commit","-a","-m","changed dependent's permissions"])
  0

  >>> update.update(["all","--accept"])
  Updating...
  Updated repository file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  dependent would like to add/change the following permissions:
     - To access to the following user directories: '~/Images' '~/Downloads'
  dependent no longer needs the following permissions:
     - To access to your soundcard, can play sounds/record sound.
  A - Accept and apply changes
  E - Apply changes and edit result
  e - Ignore request and edit permissions by hand
  A
  Checking if images need to be updated or installed...
  Checking if subuser dependent is up to date.
  Checking for updates to: dependency1@file:///home/travis/remote-test-repo
  Checking for updates to: intermediary@file:///home/travis/remote-test-repo
  Checking for updates to: dependent@file:///home/travis/remote-test-repo
  Checking if subuser foo is up to date.
  Checking for updates to: foo@default
  Running garbage collector on temporary repositories...

  Now we change the ImageSource for the ``intermediary`` image.

  >>> with open("/home/travis/test-home/.subuser/repositories/1/images/intermediary/docker-image/SubuserImagefile",mode="w") as subuserImagefile:
  ...   _ = subuserImagefile.write("FROM-SUBUSER-IMAGE dependency2")

  And commit the changes to git.

  >>> repo1.run(["commit","-a","-m","changed dependency for intermediate from dependency1 to dependency2"])
  0

  Running an update after a change installs new images and registers them with their subusers.  But it does not delete the old ones.

  >>> update.update(["all","--accept"])
  Updating...
  Updated repository file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Checking if subuser dependent is up to date.
  Installing dependency2 ...
  Building...
  Building...
  Building...
  Successfully built 21
  Building...
  Building...
  Building...
  Successfully built 22
  Installing intermediary ...
  Building...
  Building...
  Building...
  Successfully built 23
  Building...
  Building...
  Building...
  Successfully built 24
  Installing dependent ...
  Building...
  Building...
  Building...
  Successfully built 25
  Building...
  Building...
  Building...
  Successfully built 26
  Installed new image <26> for subuser dependent
  Checking if subuser foo is up to date.
  Checking for updates to: foo@default
  Running garbage collector on temporary repositories...

  >>> user = User()
  >>> set(user.getRegistry().getSubusers().keys()) == set(['dependent', u'foo'])
  True

  >>> set([i.getImageSourceName() for i in user.getInstalledImages().values()]) == set([u'foo', u'dependency1', u'bar', u'dependent', u'intermediary', u'intermediary', u'dependency2', u'dependent'])
  True

  Old images are not deleted so that update lock-subuser-to and update rollback still work. In this example, dependency1 stays installed.

  Now we lock the dependent subuser and try changing it again.

  >>> update.update(["lock-subuser-to","dependent","HEAD"])
  Locking subuser dependent to commit: HEAD
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Running garbage collector on temporary repositories...

  >>> with open("/home/travis/test-home/.subuser/repositories/1/images/intermediary/docker-image/SubuserImagefile",mode="w") as subuserImagefile:
  ...   _ = subuserImagefile.write("FROM-SUBUSER-IMAGE dependency3")

  And commit the changes to git.

  >>> repo1.run(["commit","-a","-m","changed dependency for intermediate from dependency2 to dependency3"])
  0

  Running an update after a change does nothing because the affected subuser is locked.

  >>> update.update(["all","--accept"])
  Updating...
  Updated repository file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Checking if subuser foo is up to date.
  Checking for updates to: foo@default
  Running garbage collector on temporary repositories...

  >>> user = User()
  >>> set(user.getRegistry().getSubusers().keys()) == set(['dependent', u'foo'])
  True

  >>> set([i.getImageSourceName() for i in user.getInstalledImages().values()]) == set([u'foo', u'dependency1', u'bar', u'dependent', u'intermediary', u'intermediary', u'dependency2', u'dependent'])
  True

  When we unlock the subuser it gets updated imediately.

  >>> update.update(["unlock-subuser","--accept","dependent"])
  Unlocking subuser dependent
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Checking if subuser dependent is up to date.
  Installing dependency3 ...
  Building...
  Building...
  Building...
  Successfully built 28
  Building...
  Building...
  Building...
  Successfully built 29
  Installing intermediary ...
  Building...
  Building...
  Building...
  Successfully built 30
  Building...
  Building...
  Building...
  Successfully built 31
  Installing dependent ...
  Building...
  Building...
  Building...
  Successfully built 32
  Building...
  Building...
  Building...
  Successfully built 33
  Installed new image <33> for subuser dependent
  Running garbage collector on temporary repositories...

  >>> user = User()
  >>> set(user.getRegistry().getSubusers().keys()) == set(['dependent', u'foo'])
  True

  >>> set([i.getImageSourceName() for i in user.getInstalledImages().values()]) == set([u'foo', u'dependency1', u'bar', u'dependent', u'intermediary', u'intermediary', u'dependency2',u'dependency3', u'dependent'])
  True
  """
  options,args = parseCliArgs(realArgs)
  user = User()
  permissionsAccepter = AcceptPermissionsAtCLI(user,alwaysAccept = options.accept)
  if len(args) < 1:
    sys.exit("No arguments given. Please use subuser update -h for help.")
  elif ["all"] == args:
    try:
      with user.getRegistry().getLock():
        subuserlib.update.all(user,permissionsAccepter=permissionsAccepter)
    except subuserlib.portalocker.portalocker.LockException:
      sys.exit("Another subuser process is currently running and has a lock on the registry. Please try again later.")
  elif "subusers" == args[0]:
    try:
      with user.getRegistry().getLock():
        subuserlib.update.subusers(user,args[1:],permissionsAccepter=permissionsAccepter)
    except subuserlib.portalocker.portalocker.LockException:
      sys.exit("Another subuser process is currently running and has a lock on the registry. Please try again later.")
  elif ["log"] == args:
    subuserlib.update.showLog(user)
  elif "lock-subuser-to" == args[0]:
    try:
      subuserName = args[1]
      commit = args[2]
    except KeyError:
      sys.exit("Wrong number of arguments.  Expected a subuser name and a commit.  Try running\nsubuser update --help\n for more info.")
    try:
      with user.getRegistry().getLock():
        subuserlib.update.lockSubuser(user,subuserName=subuserName,commit=commit)
    except subuserlib.portalocker.portalocker.LockException:
      sys.exit("Another subuser process is currently running and has a lock on the registry. Please try again later.")
  elif "unlock-subuser" == args[0]:
    try:
      subuserName = args[1]
    except KeyError:
      sys.exit("Wrong number of arguments.  Expected a subuser's name. Try running\nsubuser update --help\nfor more information.")
    try:
      with user.getRegistry().getLock():
        subuserlib.update.unlockSubuser(user,subuserName=subuserName,permissionsAccepter=permissionsAccepter)
    except subuserlib.portalocker.portalocker.LockException:
      sys.exit("Another subuser process is currently running and has a lock on the registry. Please try again later.")
  elif "rollback" == args[0]:
    try:
      commit = args[1]
    except KeyError:
      sys.exit("Wrong number of arguments.  Expected a commit.  Try running \nsubuser update --help\nfor more info.")
    try:
      with user.getRegistry().getLock():
        subuserlib.update.rollback(user,commit=commit)
    except subuserlib.portalocker.portalocker.LockException:
      sys.exit("Another subuser process is currently running and has a lock on the registry. Please try again later.")
  elif len(args) == 1:
    sys.exit(" ".join(args) + " is not a valid update subcommand. Please use subuser update -h for help.")
  else:
    sys.exit(" ".join(args) + " is not a valid update subcommand. Please use subuser update -h for help.")

if __name__ == "__main__":
  try:
    update(sys.argv[1:])
  except KeyboardInterrupt:
    pass
