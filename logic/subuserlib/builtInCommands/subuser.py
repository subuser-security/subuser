#!/usr/bin/python3
# -*- coding: utf-8 -*-
#external imports
import sys
import optparse
import os
#internal imports
from subuserlib.classes.user import LockedUser
from subuserlib.classes.permissionsAccepters.acceptPermissionsAtCLI import AcceptPermissionsAtCLI
import subuserlib.commandLineArguments
import subuserlib.subuser
import subuserlib.verify
import subuserlib.profile

def parseCliArgs(sysargs):
  usage = "usage: subuser subuser [add|remove|add-to-path|remove-from-path|edit-permissions|expose-entrypoints|hide-entrypoints|change-image] NAME [IMAGESOURCE]"
  description = """

Add and remove subusers.  Create shorcuts for launching subusers.

EXAMPLES:

Add a new subuser named foo based on the image image-name@repository.

    $ subuser subuser add foo image-name@repository

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

Change which image the subuser is associated with.

    $ subuser subuser change-image foo image-name@repository
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--prefix",dest="prefix",default=None,help="When removing subusers, remove all subusers who's names start with prefix.")
  parser.add_option("--home-dir",dest="homeDir",default=None,help="When adding a subuser set its home dir on the host to a non-default location.")
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
  lockedUser = LockedUser()
  with lockedUser as user:
    user.registry.commit_message = " ".join(["subuser","subuser"]+sysargs)
    permissionsAccepter = AcceptPermissionsAtCLI(user,alwaysAccept = options.accept)
    if action == "add" or action == "change-image":
      if not len(args) == 3:
        sys.exit("Wrong number of arguments to add.  See `subuser subuser -h`.")
      subuserName = args[1]
      imageSourceId = args[2]
      if action == "add":
        if options.homeDir is not None:
          homeDir = os.path.expanduser(options.homeDir)
        else:
          homeDir = None
        subuserlib.subuser.add(user,subuserName,imageSourceId,permissionsAccepter=permissionsAccepter,prompt=options.prompt,forceInternal=options.forceInternal,homeDir=homeDir)
      elif action == "change-image":
        subuserlib.subuser.changeImage(user,subuserName,imageSourceId,permissionsAccepter=permissionsAccepter,prompt=options.prompt)
    else:
      subuserNames = list(set(args[1:]))
      subusers = []
      if not options.prefix is None:
        allSubuserNames = user.registry.subusers.keys()
        subuserNames.extend([subuserName for subuserName in allSubuserNames if subuserName.startswith(options.prefix)])
      for subuserName in subuserNames:
        try:
          subusers.append(user.registry.subusers[subuserName])
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
        user.registry.logChange("Edit the permissions of:"+ " ".join(subuserNames))
        for subuser in subusers:
          subuser.editPermissionsCLI()
        subuserlib.verify.verify(user,subusers=subusers,permissionsAccepter=permissionsAccepter,prompt=options.prompt)
        user.registry.commit()
        sys.exit()
      sys.exit("Action "+args[0]+" does not exist. Try:\n subuser subuser --help")
