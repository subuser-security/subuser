#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import pathConfig
#external imports
import sys
import optparse
#internal imports
import subuserlib.classes.user
import subuserlib.commandLineArguments
import subuserlib.subuser

def parseCliArgs(sysargs):
  usage = "usage: subuser %prog [add|remove|create-shortcut] NAME IMAGESOURCE"
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
  Checking if subuser bar is up to date.
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
  Checking if subuser foo is up to date.
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
  Checking if subuser foo is up to date.
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
  Checking if subuser bar is up to date.
  Installing bar ...
  Building...
  Building...
  Building...
  Successfully built 8
  Building...
  Building...
  Building...
  Successfully built 9
  Installed new image <9> for subuser bar
  Checking if subuser foo is up to date.
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
  Checking if subuser foo is up to date.
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
  Checking if subuser broken-syntax is up to date.
  Error while building image: Error in broken-syntax's SubuserImagefile on line 0
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
  Checking if subuser broken-non-existant-dependency is up to date.
  Error while building image: Error in broken-non-existant-dependency's SubuserImagefile on line 0
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
    try:
      with user.getRegistry().getLock():
        subuserlib.subuser.add(user,name,imageSourceId)
    except subuserlib.portalocker.portalocker.LockException:
      sys.exit("Another subuser process is currently running and has a lock on the registry. Please try again later.")

  elif action == "remove":
    names = args[1:]
    try:
      with user.getRegistry().getLock():
        subuserlib.subuser.remove(user,names)
    except subuserlib.portalocker.portalocker.LockException:
      sys.exit("Another subuser process is currently running and has a lock on the registry. Please try again later.")
 
  elif action == "create-shortcut":
    name = args[1]
    try:
      with user.getRegistry().getLock():
        subuserlib.subuser.setExecutableShortcutInstalled(user,name,True)
    except subuserlib.portalocker.portalocker.LockException:
      sys.exit("Another subuser process is currently running and has a lock on the registry. Please try again later.")
  elif action == "remove-shortcut":
    name = args[1]
    try:
      with user.getRegistry().getLock():
        subuserlib.subuser.setExecutableShortcutInstalled(user,name,False)
    except subuserlib.portalocker.portalocker.LockException:
      sys.exit("Another subuser process is currently running and has a lock on the registry. Please try again later.")
  else:
    sys.exit("Action "+args[0]+" does not exist. Try:\n subuser subuser --help")
#################################################################################################

if __name__ == "__main__":
  subuser(sys.argv[1:])
