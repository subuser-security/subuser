#!/usr/bin/python3
# -*- coding: utf-8 -*-
#external imports
import sys
import optparse
#internal imports
from subuserlib.classes.user import LockedUser
import subuserlib.verify
import subuserlib.commandLineArguments
import subuserlib.profile
from subuserlib.classes.permissionsAccepters.acceptPermissionsAtCLI import AcceptPermissionsAtCLI

####################################################
def parseCliArgs(realArgs):
  usage = "usage: subuser repair [options]"
  description = """
Repair your subuser installation.

This is usefull when migrating from one machine to another.  You can copy your ~/.subuser folder to the new machine and run repair, and things should just work.
"""
  parser = optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--accept",dest="accept",action="store_true",default=False,help="Acceppt permissions without asking.")
  parser.add_option("--prompt",dest="prompt",action="store_true",default=False,help="Prompt before installing new images.")
  return parser.parse_args(args=realArgs)

@subuserlib.profile.do_cprofile
def runCommand(realArgs):
  options,arguments=parseCliArgs(realArgs)
  lockedUser = LockedUser()
  with lockedUser as user:
    user.registry.commit_message = " ".join(["subuser","repair"]+realArgs)
    permissionsAccepter = AcceptPermissionsAtCLI(user,alwaysAccept = options.accept)
    subusers = user.registry.subusers.getSortedList()
    subuserlib.verify.verify(user,subusers=subusers,permissionsAccepter=permissionsAccepter,prompt=options.prompt)
    user.registry.commit()
