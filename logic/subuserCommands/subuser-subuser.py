#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
  usage = "usage: subuser subuser [add|remove|add-to-path|remove-from-path|edit-permissions] NAME [IMAGESOURCE]"
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
def subuser(sysargs):
  """
  Manage subusers
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
      subuserlib.subuser.add(user,name,imageSourceId,permissionsAccepter=permissionsAccepter,prompt=options.prompt,forceInternal=options.forceInternal)
  elif action == "remove":
    names = args[1:]
    if not options.prefix is None:
      allSubuserNames = user.getRegistry().getSubusers().keys()
      names.extend([subuserName for subuserName in allSubuserNames if subuserName.startswith(options.prefix)])
    with user.getRegistry().getLock():
      subusers = []
      for subuserName in names:
        try:
          subusers.append(user.getRegistry().getSubusers()[subuserName])
        except KeyError:
          sys.exit("Subuser "+subuserName+" does not exist and therefore cannot be removed. Use --help for help.")
      subuserlib.subuser.remove(user,subusers)
  elif action == "add-to-path" or action == "remove-from-path":
    name = args[1]
    try:
      subuser = user.getRegistry().getSubusers()[name]
    except KeyError:
      sys.exit("Subuser "+name+" does not exist.")
    if action == "add-to-path":
      install = True
    elif action == "remove-from-path":
      install = False
    with user.getRegistry().getLock():
      subuserlib.subuser.setExecutableShortcutInstalled(user,subuser,install)
  elif action == "edit-permissions":
    try:
      name = args[1]
    except IndexError:
      sys.exit("No subusers specified for editing. Use --help for help.")
    with user.getRegistry().getLock():
      user.getRegistry().logChange("Edit "+name+"'s permissions.")
      try:
        subuser = user.getRegistry().getSubusers()[name]
      except KeyError:
        sys.exit("Subuser "+name+" does not exist. Use --help for help.")
      subuser.editPermissionsCLI()
      subuserlib.verify.verify(user,subusers=[subuser],permissionsAccepter=permissionsAccepter,prompt=options.prompt)
      user.getRegistry().commit()
  else:
    sys.exit("Action "+args[0]+" does not exist. Try:\n subuser subuser --help")

#################################################################################################

if __name__ == "__main__":
  subuser(sys.argv[1:])
