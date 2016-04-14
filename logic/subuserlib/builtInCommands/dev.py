#!/usr/bin/python3
# -*- coding: utf-8 -*-

#external imports
import sys
import optparse
import json
import os
import uuid
import subprocess
#internal imports
import subuserlib.commandLineArguments
import subuserlib.profile
import subuserlib.paths

subuserExecutable = os.path.join(subuserlib.paths.getSubuserDir(),"logic","subuser")

def parseCliArgs(realArgs):
  usage = "usage: subuser dev <args> DEV-IMAGE-NAME"
  description = """ Create and run a subuser related to a dev image.
  """
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--ls",dest="ls",action="store_true",default=False,help="List dev images.")
  parser.add_option("--update",dest="update",action="store_true",default=False,help="Update dev images associated with this folder. Note: This always uses the layer cache. Use subuser update all to update fully without layer caching.")
  parser.add_option("--remove",dest="remove",action="store_true",default=False,help="Remove dev images associated with this folder.")
  parser.add_option("--entrypoint",dest="entrypoint",default=None,help="Use entrypoint instead of default executable.")
  return parser.parse_args(args=realArgs)

@subuserlib.profile.do_cprofile
def runCommand(realArgs):
  options,args = parseCliArgs(realArgs)
  if options.ls:
    subprocess.call([subuserExecutable,"list","available","./"])
    sys.exit()
  devSubuserRegistry = ".subuser-dev"
  devSubusers = {}
  subuserNames = []
  if os.path.exists(devSubuserRegistry):
    with open(devSubuserRegistry,"r") as fd:
      devSubusers = json.load(fd)
  for devSubuser in devSubusers.values():
    subuserNames.append(devSubuser)

  if options.remove:
    subprocess.call([subuserExecutable,"subuser","remove"]+subuserNames)
    sys.exit()

  if options.update:
    if not subprocess.call([subuserExecutable,"update","--use-cache","subusers"]+subuserNames) == 0:
      sys.exit()

  if len(args) != 1:
    if options.update:
      sys.exit()
    sys.exit("Please pass a single dev image name. Use --help for help.")
  devSubuser = None
  devImage = args[0]
  if not devImage.endswith("-dev"):
    devImage = devImage + "-dev"
  try:
    devSubuser = devSubusers[devImage]
  except KeyError:
    pass
  if devSubuser is None:
    devSubuser = devImage+"@"+os.path.split(os.path.dirname(os.getcwd()+os.sep))[1]+"-"+str(uuid.uuid4())
    if subprocess.call([subuserExecutable,"subuser","add",devSubuser,devImage+"@./"]) == 0:
      devSubusers[devImage] = devSubuser
      with open(devSubuserRegistry,"w") as fd:
        json.dump(devSubusers,fd)
  if options.entrypoint is None:
    subprocess.call([subuserExecutable,"run",devSubuser])
  else:
    subprocess.call([subuserExecutable,"run","--entrypoint="+options.entrypoint,devSubuser])
