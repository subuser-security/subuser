#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import optparse

import subuserlib.installTime,subuserlib.commandLineArguments

def parseCliArgs():
  usage = "usage: subuser %prog PROGRAM_NAME(s)"
  description = """
Mark a program as needing to be updated.  Note, that this may mess up the formatting of it's permissions.json file.  This command is usefull mainly to the maintainers of subuser.  We use this command when we update a package or hear that it has been updated up stream.  The effect of this command, is that the program will be updated when the user issues `subuser update all`. 

EXAMPLE:

$ subuser mark-as-needing-update firefox
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args()

#################################################################################################

options,programNames = parseCliArgs()

for program in programNames:
  subuserlib.installTime.markProgramAsNeedingUpdate(program)