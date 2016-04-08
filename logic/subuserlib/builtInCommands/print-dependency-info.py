#!/usr/bin/python3
# -*- coding: utf-8 -*-
#external imports
import sys
import optparse
#internal imports
import subuserlib.classes.user
import subuserlib.resolve
import subuserlib.commandLineArguments
import subuserlib.profile
import subuserlib.classes.installationTask
import subuserlib.print

def parseCliArgs(realArgs):
  usage = "usage: subuser print-dependency-info IMAGE_NAME(s) SETS_OF_IMAGES"
  description = """Prints information about how the listed images relate to each other:

Example:

    $ subuser print-dependency-info foo@default
"""
  parser = optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args(args=realArgs)

@subuserlib.profile.do_cprofile
def runCommand(realArgs):
  """
  Print the dependencies of the listed progam sources.
  """
  (options,imageSourceIds) = parseCliArgs(realArgs)
  if len(imageSourceIds) == 0:
    sys.exit("No images specified.  Issue this command with -h to view help.")
  user = subuserlib.classes.user.User()
  for imageSourceId in imageSourceIds:
    try:
      imageSource = subuserlib.resolve.resolveImageSource(user,imageSourceId)
    except KeyError:
      sys.exit("The image "+imageSourceId+" does not exist.")
    indent = 0
    for imageSourceInLineage in subuserlib.classes.installationTask.getTargetLineage(imageSource):
      displayLine = (" "*indent) + imageSourceInLineage.getIdentifier()
      subuserlib.print.printWithoutCrashing(displayLine)
      indent = indent + 1
