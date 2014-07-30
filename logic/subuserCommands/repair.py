#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import sys,optparse
#internal imports
import subuserlib.registry,subuserlib.dockerImages,subuserlib.install,subuserlib.subprocessExtras,subuserlib.commandLineArguments

####################################################
def parseCliArgs():
  usage = "usage: subuser %prog [options]"
  description = """ Install all of the programs that were installed on a previous system, given that you backed up the installed-programs.json file.

Your installed-programs.js file must be in the right place.  It should probably be in ~/subuser/.  If you have a ~/.subuser/config.json file, or an /etc/subuser/config.json file, then you should look in these files to find out where installed-programs.json should reside.

"""
  parser = optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  advancedInstallOptions = subuserlib.commandLineArguments.advancedInstallOptionsGroup(parser)
  parser.add_option_group(advancedInstallOptions)
  return parser.parse_args()

def findOutWhatShouldBeInstalledButIsnt(programsThatAreSupposedToBeInstalled):
  toInstall=[]
  for program in programsThatAreSupposedToBeInstalled:
    if not subuserlib.dockerImages.isProgramsImageInstalled(program):
      toInstall.append(program)
  return toInstall

def installFromRegistry(useCache):
  """ Installs all of the programs listed in installed-programs.json file. """
  programsThatAreSupposedToBeInstalled = subuserlib.registry.getInstalledPrograms()
  programsToInstall = findOutWhatShouldBeInstalledButIsnt(programsThatAreSupposedToBeInstalled)
  print("The following programs will be installed.")
  for program in programsToInstall:
    print(program)
  if not raw_input("Continue? [y/N]").lower()=="y":
    sys.exit()
  for program in programsToInstall:
    print("\n=== Installing "+program+" from installed-programs.json registry....\n")
    subuserlib.install.installProgramAndDependencies(program, useCache)

#################################################################################################

options,arguments=parseCliArgs()
installFromRegistry(options.useCache)
