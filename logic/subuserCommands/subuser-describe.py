#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
  import pathConfig
except ImportError:
  pass
#external imports
import sys
import optparse
#internal imports
import subuserlib.classes.user
import subuserlib.commandLineArguments
import subuserlib.resolve
import subuserlib.profile

def parseCliArgs(sysargs):
  usage = "usage: subuser describe [subuser|image] SUBUSER(s)/IMAGE(s)"
  description = """Show basic information about a subuser or image: Whether it is installed, what it's permissions are ect.

EXAMPLE:

    $ subuser describe image iceweasel
    <lots of info>

    $ subuser describe subuser iceweasel
"""
  parser = optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args(args=sysargs)

@subuserlib.profile.do_cprofile
def describe(sysargs):
  """
  Describe subusers and images.
  """
  user = subuserlib.classes.user.User()
  (options,args) = parseCliArgs(sysargs)
  if len(args) < 2:
    print("Args: '"+"' '".join(args)+"'")
    print("Wrong number of arguments.")
    #parseCliArgs(["","subuser","describe","--help"])
  elif args[0] == "image":
    for image in args[1:]:
      subuserlib.resolve.resolveImageSource(user,image).describe()
  elif args[0] == "subuser":
    for subuser in  args[1:]:
      try:
        user.getRegistry().getSubusers()[subuser].describe()
      except KeyError:
        sys.exit("Subuser "+subuser+" does not exist.")
  else:
    print("Args: '"+"' '".join(args)+"'")
    print("Option not supported.")

if __name__ == "__main__":
  describe(sys.argv[1:])
