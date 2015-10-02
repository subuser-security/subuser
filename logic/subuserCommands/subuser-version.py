#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

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
  (options,args) = parseCliArgs(realArgs)
  if options.json:
    print(json.dumps(subuserlib.version.getInfo(),indent=1,separators=(",",": ")))
  else:
    print("Subuser version: " + subuserlib.version.getSubuserVersion())
    print("Docker info:")
    for key,value in subuserlib.version.getDockerInfo().items():
      print(" "+key+": "+str(value))

#################################################################################################

if __name__ == "__main__":
  printVersion(sys.argv[1:])
 
