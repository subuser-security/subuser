#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import pathConfig
#external imports
import optparse,sys
#internal imports
import subuserlib.classes.user,subuserlib.resolve,subuserlib.install,subuserlib.commandLineArguments

def parseCliArgs():
  usage = "usage: subuser %prog IMAGE_NAME(s) SETS_OF_IMAGES"
  description = """Prints information about how the listed images relate to eachother:

Example:

    $ subuser print-dependency-info foo@default
"""
  parser = optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args()

def printDependencies(imageSourceIds):
 """
 Print the dependencies of the listed progam sources.

 >>> print_dependency_info = __import__("print-dependency-info")#import self
 >>> print_dependency_info.printDependencies(["foo@default"])
 foo@default
 """
 user = subuserlib.classes.user.User()

 for imageSourceId in imageSourceIds:
   imageSource = subuserlib.resolve.resolveImageSource(user,imageSourceId)
   indent = 0
   for imageSourceInLineage in subuserlib.install.getImageSourceLineage(imageSource):
     displayLine = (" "*indent) + imageSourceInLineage.getName() + "@" + imageSourceInLineage.getRepository().getName()
     print(displayLine)
     indent = indent + 1
  

#################################################################################################

if __name__ == "__main__":
  (options,args) = parseCliArgs()
  
  if len(args) == 0:
    sys.exit("No images specified.  Issue this command with -h to view help.")
  
  printDependencies(args)
   
