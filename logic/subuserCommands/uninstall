#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import optparse,sys

import subuserlib.uninstall,subuserlib.registry,subuserlib.commandLineArguments

#######################################################
def parseCliArgs():
  usage = "usage: subuser %prog PROGRAM_NAME(s)"
  description = """Uninstall subuser programs.

NOTE: this operation does not remove that program's home directory.

"""
  parser = optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args()

def checkInstalled(programName):
  if not subuserlib.registry.isProgramInstalled(programName):
    print("Could not uninstall "+programName+" program is not installed.")
    print("\nInstalled programs are: ")
    for program in subuserlib.registry.getInstalledPrograms():
      print(program)
    sys.exit("For help, call this command with the -h option.")

def ensureProgramHasNoInstalledDependents(programName):
  installedDependents = subuserlib.registry.getInstalledDependents(programName)
  if not installedDependents == []:
    print("The following programs depend upon "+programName+" you must uninstall them first.")
    for dependent in installedDependents:
      print(dependent)
    sys.exit("To view a help message, issue this command with the -h option.")

################################################################################

options,programsToUninstall = parseCliArgs()

if len(programsToUninstall) == 0:
  sys.exit("You didn't specify any programs to uninstall.  For help issue this command with the -h option.")

for programName in programsToUninstall:
  checkInstalled(programName)
  ensureProgramHasNoInstalledDependents(programName)

print("The following programs will be uninstalled.")
for programName in programsToUninstall:
 print(programName)

if raw_input("Do you want to continue[y/N]").lower()=="y":
  for programName in programsToUninstall:
    subuserlib.uninstall.uninstall(programName)