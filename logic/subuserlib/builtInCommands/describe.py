#!/usr/bin/python3
# -*- coding: utf-8 -*-

#external imports
import sys
import optparse
#internal imports
import subuserlib.classes.user
import subuserlib.commandLineArguments
import subuserlib.resolve
import subuserlib.profile
import subuserlib.print

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
def runCommand(sysargs):
  """
  Describe subusers and images.
  """
  user = subuserlib.classes.user.User()
  (options,args) = parseCliArgs(sysargs)
  if len(args) < 2:
    subuserlib.print.printWithoutCrashing("Nothing to describe. Use -h for help.")
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
    subuserlib.print.printWithoutCrashing("Args: '"+"' '".join(args)+"'")
    subuserlib.print.printWithoutCrashing("Option not supported.")
