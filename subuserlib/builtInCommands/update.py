#!/usr/bin/python3
# -*- coding: utf-8 -*-
#external imports
import sys
import optparse
#internal imports
import subuserlib.commandLineArguments
from subuserlib.classes.user import LockedUser
import subuserlib.update
import subuserlib.profile

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
  if len(args) < 1:
    sys.exit("No arguments given. Please use subuser update -h for help.")
  lockedUser = LockedUser()
  with lockedUser as user:
    user.registry.commit_message = " ".join(["subuser","update"]+realArgs)
    operation = user.operation
    operation.permissionsAccepter.alwaysAccept = options.accept
    operation.prompt = options.prompt
    operation.useCache = options.useCache
    if ["all"] == args:
      operation.subusers = list(user.registry.subusers.values())
      subuserlib.update.run(operation)
    elif "subusers" == args[0]:
      subuserNamesToUpdate = args[1:]
      try:
        operation.loadSubusersByName(subuserNamesToUpdate)
      except LookupError as le:
        sys.exit(le)
      if operation.subusers:
        subuserlib.update.run(operation)
      else:
        sys.exit("You did not specify any subusers to be updated. Use --help for help. Exiting...")
    elif "lock-subuser-to" == args[0]:
      if len(args) < 3:      
        sys.exit("Wrong number of arguments.  Expected a subuser name and a commit.  Try running\nsubuser update --help\n for more info.")
      subuserNames = args[1:-1]
      commit = args[-1]
      try:
        operation.loadSubusersByName(subuserNames)
      except LookupError as le:
        sys.exit(le)
      subuserlib.update.lockSubusers(user.operation,commit=commit)
    elif "unlock-subuser" == args[0]:
      if len(args) < 2:
        sys.exit("Wrong number of arguments.  Expected a subuser's name. Try running\nsubuser update --help\nfor more information.")
      subuserNames = args[1:]
      try:
        operation.loadSubusersByName(subuserNames)
      except LookupError as le:
        sys.exit(le)
      subuserlib.update.unlockSubusers(operation)
    elif len(args) == 1:
      sys.exit(" ".join(args) + " is not a valid update subcommand. Please use subuser update -h for help.")
    else:
      sys.exit(" ".join(args) + " is not a valid update subcommand. Please use subuser update -h for help.")
