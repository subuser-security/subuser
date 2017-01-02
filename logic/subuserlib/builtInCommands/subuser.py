#!/usr/bin/python3
# -*- coding: utf-8 -*-
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
  usage = "usage: subuser subuser [add|remove|add-to-path|remove-from-path|edit-permissions|expose-entrypoints|hide-entrypoints] NAME [IMAGESOURCE]"
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

    $ subuser subuser add-to-path foo

You can now launch foo directly.

    $ foo

Remove the launcher (if one exists) for the subuser named foo.

    $ subuser subuser remove-from-path foo

Expose a subuser's predefined entrypoints.

    $ subuser subuser expose-entrypoints haskell-platform

Now you can run the predefined entrypoints directly.

    $ gcc
    $ cabal install

To remove the entrypoints from the PATH use

    $ subuser subuser hide-entrypoints haskell-platform

Edit a subuser's permissions.

    $ subuser subuser edit-permissions foo
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--prefix",dest="prefix",default=None,help="When removing subusers, remove all subusers who's names start with prefix.")
  parser.add_option("--accept",dest="accept",action="store_true",default=False,help="Accept permissions without asking.")
  parser.add_option("--prompt",dest="prompt",action="store_true",default=False,help="Prompt before installing new images.")
  parser.add_option("--force-internal",dest="forceInternal",action="store_true",default=False,help="Force a subuser who's name starts with ! to be added, despite the fact that ! marks interal subusers and is normally forbidden.")
  return parser.parse_args(args=sysargs)

@subuserlib.profile.do_cprofile
def runCommand(sysargs):
  """
  Manage subusers
  """
  options,args = parseCliArgs(sysargs)
  try:
    action = args[0]
  except IndexError:
    print("Wrong number of arguments!")
    parseCliArgs(["--help"])
  user = User()
  user.getRegistry().commit_message = " ".join(["subuser","subuser"]+sysargs)
  permissionsAccepter = AcceptPermissionsAtCLI(user,alwaysAccept = options.accept)
  if action == "add":
    if not len(args) == 3:
      sys.exit("Wrong number of arguments to add.  See `subuser subuser -h`.")
    subuserName = args[1]
    imageSourceId = args[2]
    with user.getRegistry().getLock():
      subuserlib.subuser.add(user,subuserName,imageSourceId,permissionsAccepter=permissionsAccepter,prompt=options.prompt,forceInternal=options.forceInternal)
  else:
    subuserNames = list(set(args[1:]))
    with user.getRegistry().getLock():
      subusers = []
      if not options.prefix is None:
        allSubuserNames = user.getRegistry().getSubusers().keys()
        subuserNames.extend([subuserName for subuserName in allSubuserNames if subuserName.startswith(options.prefix)])

      for subuserName in subuserNames:
        try:
          subusers.append(user.getRegistry().getSubusers()[subuserName])
        except KeyError:
          sys.exit("Subuser "+subuserName+" does not exist. Use --help for help.")
      if subusers == []:
        sys.exit("No subusers specified. Use --help for help.")
      if action == "remove":
          subuserlib.subuser.remove(user,subusers)
          sys.exit()
      addAndRemoveCommands = [("add-to-path","remove-from-path",subuserlib.subuser.setExecutableShortcutInstalled),("expose-entrypoints","hide-entrypoints",lambda user,subusers,install:subuserlib.subuser.setEntrypointsExposed(user,subusers,install,permissionsAccepter))]
      for add,remove,command in addAndRemoveCommands:
        if action == add or action == remove:
          if action == add:
            install = True
          elif action == remove:
            install = False
          command(user,subusers,install)
          sys.exit()
      if action == "edit-permissions":
        user.getRegistry().logChange("Edit the permissions of:"+ " ".join(subuserNames))
        for subuser in subusers:
          subuser.editPermissionsCLI()
        subuserlib.verify.verify(user,subusers=subusers,permissionsAccepter=permissionsAccepter,prompt=options.prompt)
        user.getRegistry().commit()
        sys.exit()
      sys.exit("Action "+args[0]+" does not exist. Try:\n subuser subuser --help")
