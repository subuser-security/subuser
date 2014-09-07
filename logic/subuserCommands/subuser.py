#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import sys,optparse
#internal imports
import subuserlib.classes.user,subuserlib.commandLineArguments,subuserlib.subuser

def parseCliArgs():
  usage = "usage: subuser %prog [add|remove|create-shortcut] NAME IMAGESOURCE"
  description = """

Add and remove subusers.  Create shorcuts for launching subusers.

$ subuser subuser add foo foo@default

$ subuser subuser remove foo

$ subuser subuser create-shorcut foo

$ subuser subuser remove-shortcut foo
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  advancedOptions = subuserlib.commandLineArguments.advancedInstallOptionsGroup(parser)
  parser.add_option_group(advancedOptions)
  return parser.parse_args()

#################################################################################################

options,args = parseCliArgs()

action = args[0]

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

  
