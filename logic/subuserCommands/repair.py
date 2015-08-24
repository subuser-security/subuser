#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import pathConfig
#external imports
import sys
import optparse
#internal imports
from subuserlib.classes.user import User
import subuserlib.verify
import subuserlib.commandLineArguments
from subuserlib.classes.permissionsAccepters.acceptPermissionsAtCLI import AcceptPermissionsAtCLI

####################################################
def parseCliArgs(realArgs):
  usage = "usage: subuser %prog [options]"
  description = """
Repair your subuser installation.

This is usefull when migrating from one machine to another.  You can copy your ~/.subuser folder to the new machine and run repair, and things should just work.
"""
  parser = optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--accept",dest="accept",action="store_true",default=False,help="Acceppt permissions without asking.")
  return parser.parse_args(args=realArgs)

def verify(realArgs):
  options,arguments=parseCliArgs(realArgs)
  user = User()
  permissionsAccepter = AcceptPermissionsAtCLI(user,alwaysAccept = options.accept)
  try:
    with user.getRegistry().getLock() as LockFileHandle:
      subuserNames = list(user.getRegistry().getSubusers().keys())
      subuserNames.sort()
      subuserlib.verify.verify(user,subuserNames=subuserNames,permissionsAccepter=permissionsAccepter)
      user.getRegistry().commit()
  except subuserlib.portalocker.portalocker.LockException:
    sys.exit("Another subuser process is currently running and has a lock on the registry. Please try again later.")
  
if __name__ == "__main__":
  verify(sys.argv[1:])
