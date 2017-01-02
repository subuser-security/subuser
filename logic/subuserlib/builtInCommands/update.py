#!/usr/bin/python3
# -*- coding: utf-8 -*-
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
  usage = "usage: subuser update [options]"
  description = """Update subuser images.

  all
      Updates all subuser images which have been marked as out of date.

  EXAMPLE:
    $ subuser update all

  subusers
      Updates the specified subusers

  EXAMPLE:
    $ subuser update subusers iceweasel git

  lock-subuser-to SUBUSER GIT-COMMIT
      Don't want a subuser to be updated?  No problem, lock it to a given version with this update sub-command.  Use subuser update log to see a list of possible hashes.

  unlock-subuser SUBUSER
      Unlock the subuser and ensure that it is up-to-date.

"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--accept",dest="accept",action="store_true",default=False,help="Accept permissions without asking.")
  parser.add_option("--prompt",dest="prompt",action="store_true",default=False,help="Prompt before installing new images.")
  parser.add_option("--use-cache",dest="useCache",action="store_true",default=False,help="Use the layer cache when building images.")
  return parser.parse_args(args=realArgs)

#################################################################################################

@subuserlib.profile.do_cprofile
def runCommand(realArgs):
  """
  Update your subuser installation.
  """
  options,args = parseCliArgs(realArgs)
  user = User()
  user.getRegistry().commit_message = " ".join(["subuser","update"]+realArgs)
  permissionsAccepter = AcceptPermissionsAtCLI(user,alwaysAccept = options.accept)
  if len(args) < 1:
    sys.exit("No arguments given. Please use subuser update -h for help.")
  elif ["all"] == args:
    with user.getRegistry().getLock():
      subuserlib.update.all(user,permissionsAccepter=permissionsAccepter,prompt=options.prompt,useCache=options.useCache)
  elif "subusers" == args[0]:
    subuserNamesToUpdate = args[1:]
    subusersToUpdate = []
    for subuserName in subuserNamesToUpdate:
      try:
        subusersToUpdate.append(user.getRegistry().getSubusers()[subuserName])
      except KeyError:
        sys.exit("Subuser "+subuserName+" does not exist. Use --help for help.")
    if subusersToUpdate:
      with user.getRegistry().getLock():
        subuserlib.update.subusers(user,subusers=subusersToUpdate,permissionsAccepter=permissionsAccepter,prompt=options.prompt,useCache=options.useCache)
    else:
      sys.exit("You did not specify any subusers to be updated. Use --help for help. Exiting...")
  elif "lock-subuser-to" == args[0]:
    try:
      subuserName = args[1]
      commit = args[2]
    except IndexError:
      sys.exit("Wrong number of arguments.  Expected a subuser name and a commit.  Try running\nsubuser update --help\n for more info.")
    with user.getRegistry().getLock():
      try:
        subuser = user.getRegistry().getSubusers()[subuserName]
      except KeyError:
        sys.exit("Subuser "+subuserName+" does not exist and therefore cannot be locked. Use --help for help.")
      subuserlib.update.lockSubuser(user,subuser=subuser,commit=commit)
  elif "unlock-subuser" == args[0]:
    try:
      subuserName = args[1]
    except IndexError:
      sys.exit("Wrong number of arguments.  Expected a subuser's name. Try running\nsubuser update --help\nfor more information.")
    try:
      subuser = user.getRegistry().getSubusers()[subuserName]
    except KeyError:
      sys.exit("Subuser "+subuserName+" does not exist. Cannot lock. Use --help for help.")
    with user.getRegistry().getLock():
      subuserlib.update.unlockSubuser(user,subuser=subuser,permissionsAccepter=permissionsAccepter,prompt=options.prompt)
  elif len(args) == 1:
    sys.exit(" ".join(args) + " is not a valid update subcommand. Please use subuser update -h for help.")
  else:
    sys.exit(" ".join(args) + " is not a valid update subcommand. Please use subuser update -h for help.")
