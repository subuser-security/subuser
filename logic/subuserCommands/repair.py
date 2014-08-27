#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import optparse
#internal imports
import subuserlib.classes.user,subuserlib.verify

####################################################
def parseCliArgs():
  usage = "usage: subuser %prog [options]"
  description = """
Repair your subuser installation.

This is usefull when migrating from one machine to another.  You can copy your ~/.subuser folder to the new machine and run repair, and things should just work.
"""
  parser = optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  advancedInstallOptions = subuserlib.commandLineArguments.advancedInstallOptionsGroup(parser)
  parser.add_option_group(advancedInstallOptions)
  return parser.parse_args()

options,arguments=parseCliArgs()

user = subuserlib.classes.user.User()
subuserlib.verify.verify(user)
user.getRegistry().commit()
