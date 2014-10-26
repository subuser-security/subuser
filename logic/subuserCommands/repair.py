#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import pathConfig
#external imports
import optparse,sys
#internal imports
import subuserlib.classes.user,subuserlib.verify,subuserlib.commandLineArguments

####################################################
def parseCliArgs(realArgs):
  usage = "usage: subuser %prog [options]"
  description = """
Repair your subuser installation.

This is usefull when migrating from one machine to another.  You can copy your ~/.subuser folder to the new machine and run repair, and things should just work.
"""
  parser = optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args(args=realArgs)

def verify(realArgs):
  options,arguments=parseCliArgs(realArgs)
  user = subuserlib.classes.user.User()
  subuserlib.verify.verify(user)
  user.getRegistry().commit()

if __name__ == "__main__":
  verify(sys.argv[1:])

