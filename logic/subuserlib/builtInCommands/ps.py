#!/usr/bin/python3
# -*- coding: utf-8 -*-

#external imports
import sys
import optparse
import json
import os
import uuid
#internal imports
from subuserlib.classes.user import User
import subuserlib.commandLineArguments
import subuserlib.profile

def parseCliArgs(realArgs):
  usage = "usage: subuser ps"
  description = """ List running subusers.
  """
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--internal",dest="internal",action="store_true",default=False,help="Include internal subusers in list.")
  return parser.parse_args(args=realArgs)

@subuserlib.profile.do_cprofile
def runCommand(realArgs):
  options,args = parseCliArgs(realArgs)
  user = User()
  runningImages = [container["Image"] for container in user.getDockerDaemon().getContainers(onlyRunning=True)]
  for _,subuser in user.getRegistry().getSubusers().items():
    try:
      if subuser.getRunReadyImage().getId() in runningImages:
        if not options.internal:
          if subuser.getName().startswith("!"):
            continue
        print(subuser.getName())
    except (KeyError,subuserlib.classes.subuserSubmodules.run.runtimeCache.NoRuntimeCacheForSubusersWhichDontHaveExistantImagesException):
      pass
