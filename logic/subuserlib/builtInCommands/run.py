#!/usr/bin/python3
# -*- coding: utf-8 -*-
#external imports
import sys
import optparse
import os
#internal imports
from subuserlib.classes.user import User
import subuserlib.commandLineArguments
import subuserlib.profile

##############################################################
def parseCliArgs(sysargs):
  usage = "usage: subuser run [arguments-for-run-command] SUBUSER-NAME [arguments-for-subuser]"
  description = """Run the given subuser.

For example:

    $ subuser run iceweasel

Will launch the subuser named iceweasel

To launch the subuser with another executable than it's default use the ``--entrypoint`` option.

If the SUBUSER_EXTRA_DOCKER_ARGS environment variable is set. Those arguments will be passed to Docker.
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--entrypoint", dest="entrypoint",default=None,help="Override the default executable for this subuser.")
  parser.add_option("--dry", dest="dry",action="store_true",default=False,help="Dry run, only display what commands would be called by subuser, don't actually run anything.")
  return parser.parse_args(args=sysargs)

class ArgParser():
  def __init__(self):
    self.preArgs = []
    self.subuserName = None
    self.subuserArgs = []
    self.consumedSubuserName = False

  def readArg(self,arg):
    if not self.consumedSubuserName:
      if arg.startswith("-"):
        self.preArgs.append(arg)
      else:
        self.subuserName = arg
        self.consumedSubuserName = True
    else:
      self.subuserArgs.append(arg)

#################################################################################################

@subuserlib.profile.do_cprofile
def runCommand(args):
  preArgs = []
  argParser = ArgParser()
  for arg in args:
    argParser.readArg(arg)

  if not argParser.consumedSubuserName:
    print("Subuser name not listed.")
    parseCliArgs(["--help"])

  options,_ = parseCliArgs(argParser.preArgs)

  user = User()
  if not "SUBUSER_VERBOSITY" in os.environ:
    user.getRegistry().setLogOutputVerbosity(0)
  if argParser.subuserName in user.getRegistry().getSubusers():
    try:
      extraDockerFlags = os.environ["SUBUSER_EXTRA_DOCKER_ARGS"].split(" ")
    except KeyError:
      extraDockerFlags = []
    try:
      subuser = user.getRegistry().getSubusers()[argParser.subuserName]
      runtime = subuser.getRuntime(os.environ,extraDockerFlags=extraDockerFlags,entrypoint=options.entrypoint)
      if runtime:
        if not options.dry:
          runtime.run(argParser.subuserArgs)
        else:
          if subuser.getImageId():
            print("The image will be prepared using the Dockerfile:")
            print(subuser.getRunReadyImage().generateImagePreparationDockerfile())
            print("The command to launch the image is:")
            print(runtime.getPrettyCommand(argParser.subuserArgs))
          else:
            sys.exit("There is no installed image for this subuser. Cannot run.")
      else:
        sys.exit("The subuser's image failed to build. Please use the subuser registry log and subuser repair commands for more information.")
    except (subuserlib.classes.subuser.SubuserHasNoPermissionsException,subuserlib.classes.subuserSubmodules.run.runtimeCache.NoRuntimeCacheForSubusersWhichDontHaveExistantImagesException) as e:
      sys.exit(str(e))
  else:
    sys.exit(argParser.subuserName + " not found.\nUse --help for help.")
