#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import pathConfig
#external imports
import sys
import optparse
#internal imports
import subuserlib.classes.user
import subuserlib.resolve
import subuserlib.install
import subuserlib.commandLineArguments

def parseCliArgs(realArgs):
  usage = "usage: subuser %prog IMAGE_NAME(s) SETS_OF_IMAGES"
  description = """Prints information about how the listed images relate to each other:

Example:

    $ subuser print-dependency-info foo@default
"""
  parser = optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args(args=realArgs)

def printDependencies(realArgs):
  """
  Print the dependencies of the listed progam sources.
 
  Tests
  -----
 
  **Setup:**
  >>> print_dependency_info = __import__("print-dependency-info")#import self
 
  Prints a list of images that the image depends on, including itself.
 
  >>> print_dependency_info.printDependencies(["foo@default"])
  foo@default
 
  If the image doesn't exist, tell us.
 
  >>> try:
  ...  print_dependency_info.printDependencies(["non-existant@default"])
  ... except SystemExit as e:
  ...  print(e)
  The image non-existant@default does not exist.
 
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
    for imageSourceInLineage in subuserlib.install.getImageSourceLineage(imageSource):
      displayLine = (" "*indent) + imageSourceInLineage.getIdentifier()
      print(displayLine)
      indent = indent + 1

#################################################################################################

if __name__ == "__main__":
  printDependencies(sys.argv[1:])
 
