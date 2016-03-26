#!/usr/bin/python3
# -*- coding: utf-8 -*-
try:
  import pathConfig
except ImportError:
  pass
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

try:
  subuserExecutable = os.environ["SUBUSER_EXECUTABLE"]
except KeyError:
  subuserExecutable = "subuser"

def parseCliArgs(realArgs):
  usage = "usage: subuser dev <args> DEV-IMAGE-NAME"
  description = """ Create and run a subuser related to a dev image.
  """
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--ls",dest="ls",action="store_true",default=False,help="List dev images.")
  parser.add_option("--remove",dest="remove",action="store_true",default=False,help="Remove dev images associated with this folder.")
  parser.add_option("--entrypoint",dest="entrypoint",default=None,help="Use entrypoint instead of default executable.")
  return parser.parse_args(args=realArgs)

@subuserlib.profile.do_cprofile
def dev(realArgs):
  options,args = parseCliArgs(realArgs)
  if options.ls:
    subprocess.call([subuserExecutable,"list","available","./"])
    sys.exit()
  devSubuserRegistry = ".subuser-dev"
  devSubusers = {}
  if options.remove:
    subusers = []
    if os.path.exists(devSubuserRegistry):
      with open(devSubuserRegistry,"r") as fd:
        devSubusers = json.load(fd)
    for devSubuser in devSubusers.values():
      subusers.append(devSubuser)
    subprocess.call([subuserExecutable,"subuser","remove"]+subusers)
    sys.exit()
  if len(args) != 1:
    sys.exit("Please pass a single dev image name. Use --help for help.")
  devSubuser = None
  devImage = args[0]
  if not devImage.endswith("-dev"):
    devImage = devImage + "-dev"
  if os.path.exists(devSubuserRegistry):
    with open(devSubuserRegistry,"r") as fd:
      devSubusers = json.load(fd)
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

#################################################################################################

if __name__ == "__main__":
  dev(sys.argv[1:])
