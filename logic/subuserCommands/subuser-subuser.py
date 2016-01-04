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
