#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

try:
  import pathConfig
except ImportError:
  pass
#external imports
import sys
import optparse
import os
#internal imports
from subuserlib.classes.user import User
from subuserlib.classes.permissionsAccepters.acceptPermissionsAtCLI import AcceptPermissionsAtCLI
import subuserlib.commandLineArguments
import subuserlib.subuser
import subuserlib.verify
import subuserlib.profile

def parseCliArgs(sysargs):
  usage = "usage: subuser subuser [add|remove|create-shortcut|remove-shortcut|edit-permissions] NAME [IMAGESOURCE]"
  description = """

Add and remove subusers.  Create shorcuts for launching subusers.

EXAMPLES:

Add a new subuser named foo based on the image foo@default.

    $ subuser subuser add foo foo@default

Remove the subuser named foo.

    $ subuser subuser remove foo

Remove subusers foo and bar.

    $ subuser subuser remove foo bar

Create a launcher for the subuser named foo.

    $ subuser subuser create-shorcut foo

You can now launch foo directly.

    $ foo

Remove the launcher (if one exists) for the subuser named foo.

    $ subuser subuser remove-shortcut foo

Edit a subuser's permissions.

    $ subuser subuser edit-permissions foo
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--prefix",dest="prefix",default=None,help="When removing subusers, remove all subusers who's names start with prefix.")
  parser.add_option("--accept",dest="accept",action="store_true",default=False,help="Accept permissions without asking.")
  parser.add_option("--prompt",dest="prompt",action="store_true",default=False,help="Prompt before installing new images.")
  return parser.parse_args(args=sysargs)

@subuserlib.profile.do_cprofile
def subuser(sysargs):
  """
  Manage subusers

  Tests
  -----

  **Setup:**

  >>> subuser = __import__("subuser-subuser") #import self
  >>> import subuserlib.classes.user

  At the start of our tests, the test environment has one subuser named ``foo``.

  >>> user = User()
  >>> set(user.getRegistry().getSubusers().keys()) == set([u'foo'])
  True

  We add another subuser named ``bar``.

  >>> subuser.subuser(["add","--accept","bar","bar@file:///home/travis/remote-test-repo"])
  Adding subuser bar bar@file:///home/travis/remote-test-repo
  Adding new temporary repository file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  bar would like to have the following permissions:
   Description: bar
   Maintainer: fred
   Executable: /usr/bin/bar
  A - Accept and apply changes
  E - Apply changes and edit result
  A
  Checking if images need to be updated or installed...
  Checking if subuser bar is up to date.
  New images for the following subusers need to be installed:
  bar
  Installing bar ...
  Building...
  Building...
  Building...
  Successfully built 6
  Building...
  Building...
  Building...
  Successfully built 7
  Installed new image <7> for subuser bar
  Running garbage collector on temporary repositories...

  Now we have two subusers.

  >>> user = User()
  >>> set(user.getRegistry().getSubusers().keys()) == set([u'foo', 'bar'])
  True

  We remove ``bar``.

  >>> subuser.subuser(["remove","bar"])
  Removing subuser bar
   If you wish to remove the subusers image, issue the command $ subuser remove-old-images
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Running garbage collector on temporary repositories...

  Now we only have one subuser.

  >>> user = User()
  >>> set(user.getRegistry().getSubusers().keys()) == set([u'foo'])
  True

  We add another subuser named ``bar`` using a local folder rather than from a git repo.

  >>> subuser.subuser(["add","--accept","bar","bar@/home/travis/remote-test-repo"])
  Adding subuser bar bar@/home/travis/remote-test-repo
  Adding new temporary repository /home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  bar would like to have the following permissions:
   Description: bar
   Maintainer: fred
   Executable: /usr/bin/bar
  A - Accept and apply changes
  E - Apply changes and edit result
  A
  Checking if images need to be updated or installed...
  Checking if subuser bar is up to date.
  New images for the following subusers need to be installed:
  bar
  Installing bar ...
  Building...
  Building...
  Building...
  Successfully built 10
  Building...
  Building...
  Building...
  Successfully built 11
  Installed new image <11> for subuser bar
  Running garbage collector on temporary repositories...

  Now we have two subusers.

  >>> user = User()
  >>> set(user.getRegistry().getSubusers().keys()) == set([u'foo', 'bar'])
  True

  We remove ``bar``.

  >>> subuser.subuser(["remove","bar"])
  Removing subuser bar
   If you wish to remove the subusers image, issue the command $ subuser remove-old-images
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Running garbage collector on temporary repositories...

  Now we only have one subuser.

  >>> user = User()
  >>> set(user.getRegistry().getSubusers().keys()) == set([u'foo'])
  True

  If we try adding a subuser which fails to install do to a bad ``SubuserImagefile`` an error is displayed, a cleanup process occures, and nothing terribly bad happens.

  This works for syntax errors.

  >>> subuser.subuser(["add","--accept","broken-syntax","broken-syntax@file:///home/travis/remote-test-repo"])
  Adding subuser broken-syntax broken-syntax@file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  broken-syntax would like to have the following permissions:
   Description: broken-syntax
   Maintainer: fred
   Is a library.
  A - Accept and apply changes
  E - Apply changes and edit result
  A
  Checking if images need to be updated or installed...
  Checking if subuser broken-syntax is up to date.
  Error in broken-syntax's SubuserImagefile on line 0
   Subuser image does not exist: ""
  Images for the following subusers failed to build:
  broken-syntax
  Running garbage collector on temporary repositories...

  >>> subuser.subuser(["add","--accept","broken-non-existant-dependency","broken-non-existant-dependency@file:///home/travis/remote-test-repo"])
  Adding subuser broken-non-existant-dependency broken-non-existant-dependency@file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  broken-non-existant-dependency would like to have the following permissions:
   Description: broken-non-existant-dependency
   Maintainer: fred
   Is a library.
  A - Accept and apply changes
  E - Apply changes and edit result
  A
  Checking if images need to be updated or installed...
  Checking if subuser broken-non-existant-dependency is up to date.
  Error in broken-non-existant-dependency's SubuserImagefile on line 0
   Subuser image does not exist: "non-existant-I-do-not-exist!!!!!"
  Images for the following subusers failed to build:
  broken-non-existant-dependency
  Running garbage collector on temporary repositories...

  >>> subuser.subuser(["add","--accept","broken-permissions-file","broken-permissions-file@file:///home/travis/remote-test-repo"])
  Adding subuser broken-permissions-file broken-permissions-file@file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Error, user dir permissions may not contain system wide absolute paths. The user dir: "/etc/" is forbidden.
  Running garbage collector on temporary repositories...

  >>> subuser.subuser(["remove","broken-syntax","broken-non-existant-dependency","broken-permissions-file"])
  Removing subuser broken-syntax
   If you wish to remove the subusers image, issue the command $ subuser remove-old-images
  Removing subuser broken-non-existant-dependency
   If you wish to remove the subusers image, issue the command $ subuser remove-old-images
  Removing subuser broken-permissions-file
   If you wish to remove the subusers image, issue the command $ subuser remove-old-images
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Running garbage collector on temporary repositories...
  """
  options,args = parseCliArgs(sysargs)
  try:
    action = args[0]
  except IndexError:
    parseCliArgs(["--help"])
  user = User()
  permissionsAccepter = AcceptPermissionsAtCLI(user,alwaysAccept = options.accept)
  if action == "add":
    if not len(args) == 3:
      sys.exit("Wrong number of arguments to add.  See `subuser subuser -h`.")
    name = args[1]
    imageSourceId = args[2]
    with user.getRegistry().getLock():
      subuserlib.subuser.add(user,name,imageSourceId,permissionsAccepter=permissionsAccepter,prompt=options.prompt)
  elif action == "remove":
    names = args[1:]
    if not options.prefix is None:
      allSubuserNames = user.getRegistry().getSubusers().keys()
      names.extend([subuserName for subuserName in allSubuserNames if subuserName.startswith(options.prefix)])
    with user.getRegistry().getLock():
      subuserlib.subuser.remove(user,names)
  elif action == "create-shortcut":
    name = args[1]
    with user.getRegistry().getLock():
      subuserlib.subuser.setExecutableShortcutInstalled(user,name,True)
  elif action == "remove-shortcut":
    name = args[1]
    with user.getRegistry().getLock():
      subuserlib.subuser.setExecutableShortcutInstalled(user,name,False)
  elif action == "edit-permissions":
    name = args[1]
    with user.getRegistry().getLock():
      user.getRegistry().logChange("Edit "+name+"'s permissions.")
      subuser = user.getRegistry().getSubusers()[name]
      subuser.editPermissionsCLI()
      subuserlib.verify.verify(user,subuserNames=[name],permissionsAccepter=permissionsAccepter,prompt=options.prompt)
      user.getRegistry().commit()
  else:
    sys.exit("Action "+args[0]+" does not exist. Try:\n subuser subuser --help")

#################################################################################################

if __name__ == "__main__":
  subuser(sys.argv[1:])
