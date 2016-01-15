#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
  import pathConfig
except ImportError:
  pass
#external imports
import json
import sys
import optparse
#internal imports
import subuserlib.version
import subuserlib.commandLineArguments
import subuserlib.profile
from subuserlib.classes.user import User

def parseCliArgs(realArgs):
  usage = "usage: subuser version"
  description = """Prints subuser's version and other usefull debugging info.
"""
  parser = optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--json",dest="json",action="store_true",default=False,help="Display results in JSON format.")
  return parser.parse_args(args=realArgs)

@subuserlib.profile.do_cprofile
def printVersion(realArgs):
  """
  >>> version = __import__("subuser-version") #import self
  >>> version.printVersion([])
  Subuser version: 0.5
  Docker info:
   Foo: bar
  """
  user = User()
  (options,args) = parseCliArgs(realArgs)
  if options.json:
    print(json.dumps(subuserlib.version.getInfo(user),indent=1,separators=(",",": ")))
  else:
    print("Subuser version: " + subuserlib.version.getSubuserVersion(user))
    print("Docker info:")
    for key,value in subuserlib.version.getDockerInfo(user).items():
      print(" "+key+": "+str(value))

#################################################################################################

if __name__ == "__main__":
  printVersion(sys.argv[1:])
