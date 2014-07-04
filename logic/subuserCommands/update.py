#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

# This command updates all or some of the installed subuser programs.

import sys,optparse

import subprocess,subuserlib.update,subuserlib.install

import subuserlib.commandLineArguments


#####################################################################################

def parseCliArgs():
  usage = "usage: subuser %prog [options] PROGRAM_NAME(s)"
  description = """Update subuser-programs.

Note: You can either pass a list of program names, or you can pass the argument `all`:

  all 
      Updates all subuser-programs which have been marked as out of date.
      You should run git pull before doing this in order to get an up-to-date program list.

  EXAMPLE:
    $ subuser update all
 
Explicitly listing programs at the command line, force reinstalls the program, whether it is marked as being out of date or not.

EXAMPLE:

    $ subuser update vim firefox

Reinstalls vim and firefox.
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args()
#################################################################################################

options,args = parseCliArgs()

if ["all"] == args:
  programsToBeUpdated = list(set(programsToBeUpdated + subuserlib.update.getProgramsWhosLastUpdateTimesChanged()))
  userSpecifiedPrograms = []
else:
  programsToBeUpdated = args
  userSpecifiedPrograms = args

#Check if there is anything to do
if len(programsToBeUpdated) > 0:
  subuserlib.update.updateSomePrograms(programsToBeUpdated)
  # Ensure that all programs which we have requested be updated are still installed after the update:
  for program in userSpecifiedPrograms:
    if not subuserlib.registry.isProgramInstalled(program):
      subuserlib.install.installProgramAndDependencies(program, False)
else:
  sys.exit("""You need to specify a list of programs to be updated, or pass 'all' to update all programs.  For more info issue this command with the -h argument.""")
