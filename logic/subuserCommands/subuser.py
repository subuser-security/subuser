#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import pathConfig
#external imports
import sys,optparse
#internal imports
import subuserlib.classes.user,subuserlib.commandLineArguments,subuserlib.subuser

def parseCliArgs(sysargs):
  usage = "usage: subuser %prog [add|remove|create-shortcut] NAME IMAGESOURCE"
  description = """

Add and remove subusers.  Create shorcuts for launching subusers.

EXAMPLES:

Add a new subuser named foo based on the image foo@default.

    $ subuser subuser add foo foo@default

Remove the subuser named foo.

    $ subuser subuser remove foo

Create a launcher for the subuser named foo.

    $ subuser subuser create-shorcut foo

Remove the launcher (if one exists) for the subuser named foo.

    $ subuser subuser remove-shortcut foo
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args(args=sysargs)

def subuser(sysargs):
  """
  Manage subusers

  Tests
  -----

  **Setup:**

  >>> import subuser #import self
  >>> import subuserlib.classes.user

  At the start of our tests, the test environment has one subuser named ``foo``.

  >>> user = subuserlib.classes.user.User()
  >>> set(user.getRegistry().getSubusers().keys()) == set([u'foo'])
  True

  We add another subuser named ``bar``.

  >>> subuser.subuser(["add","bar","bar@file:///home/travis/remote-test-repo"])
  Adding subuser bar bar@file:///home/travis/remote-test-repo
  Adding new temporary repository file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Installing bar ...
  Installed new image for subuser bar
  Running garbage collector on temporary repositories...

  Now we have two subusers.

  >>> user = subuserlib.classes.user.User()
  >>> set(user.getRegistry().getSubusers().keys()) == set([u'foo', 'bar'])
  True

  We remove ``bar``.

  >>> subuser.subuser(["remove","bar"])
  Removing subuser bar
   If you wish to remove the subusers image, issue the command $ subuser remove-old-images
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Running garbage collector on temporary repositories...

  Now we only have one subuser.

  >>> user = subuserlib.classes.user.User()
  >>> set(user.getRegistry().getSubusers().keys()) == set([u'foo'])
  True

  We add another subuser named ``bar`` using a local folder rather than from a git repo.

  >>> subuser.subuser(["add","bar","bar@/home/travis/remote-test-repo"])
  Adding subuser bar bar@/home/travis/remote-test-repo
  Adding new temporary repository /home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Installing bar ...
  Installed new image for subuser bar
  Running garbage collector on temporary repositories...

  Now we have two subusers.

  >>> user = subuserlib.classes.user.User()
  >>> set(user.getRegistry().getSubusers().keys()) == set([u'foo', 'bar'])
  True

  We remove ``bar``.

  >>> subuser.subuser(["remove","bar"])
  Removing subuser bar
   If you wish to remove the subusers image, issue the command $ subuser remove-old-images
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Running garbage collector on temporary repositories...

  Now we only have one subuser.

  >>> user = subuserlib.classes.user.User()
  >>> set(user.getRegistry().getSubusers().keys()) == set([u'foo'])
  True

  If we try adding a subuser which fails to install do to a bad ``SubuserImagefile`` an error is displayed, a cleanup process occures, and nothing terribly bad happens.

  This works for syntax errors.

  >>> try:
  ...   subuser.subuser(["add","broken-syntax","broken-syntax@file:///home/travis/remote-test-repo"])
  ... except SystemExit:
  ...   pass
  Adding subuser broken-syntax broken-syntax@file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Error while building image: Error in SubuserImagefile one line 0
   Subuser image does not exist: ""
  Cleaning up.

  >>> try:
  ...   subuser.subuser(["add","broken-non-existant-dependency","broken-non-existant-dependency@file:///home/travis/remote-test-repo"])
  ... except SystemExit:
  ...   pass
  Adding subuser broken-non-existant-dependency broken-non-existant-dependency@file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Error while building image: Error in SubuserImagefile one line 0
   Subuser image does not exist: "non-existant-I-do-not-exist!!!!!"
  Cleaning up.
  """
  options,args = parseCliArgs(sysargs)
  try:
    action = args[0]
  except IndexError:
    parseCliArgs(["--help"])
  user = subuserlib.classes.user.User()
  if action == "add":
    if not len(args) == 3:
      sys.exit("Wrong number of arguments to add.  See `subuser subuser -h`.")
    name = args[1]
    imageSourceId = args[2]
    subuserlib.subuser.add(user,name,imageSourceId)
  elif action == "remove":
    name = args[1]
    subuserlib.subuser.remove(user,name)
  elif action == "create-shortcut":
    name = args[1]
    subuserlib.subuser.setExecutableShortcutInstalled(user,name,True)
  elif action == "remove-shortcut":
    name = args[1]
    subuserlib.subuser.setExecutableShortcutInstalled(user,name,False)
  else:
    sys.exit("Action "+args[0]+" does not exist. Try:\n subuser subuser --help")
#################################################################################################

if __name__ == "__main__":
  subuser(sys.argv[1:])
