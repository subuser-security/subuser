#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import pathConfig
#external imports
import sys
import optparse
#internal imports
import subuserlib.classes.user
import subuserlib.commandLineArguments
import subuserlib.testImages

def parseCliArgs(realArgs):
  usage = "usage: subuser %prog <repo-name> <image-source-names>"
  description = """ Test image sources by building and running them.

  Usage:

  1. Add a temporary local repository to build your images from:

     subuser repository add test-repo /home/timothy/current/subuser-default-repository

     Note: by specifying the path as a local directory, you do not need to commit your changes to git before testing them.

  2. Test the image sources.

     subuser test-images test-repo iceweasel vim

  3. Remove the left over images.

     subuser remove-old-images --repo=test-repo

   """
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args(args=realArgs)

def testImages(realArgs):
  """
  Test the given images.
  """
  options,args = parseCliArgs(realArgs)

  user = subuserlib.classes.user.User()

  try:
    with user.getRegistry().getLock() as lockFileHandler:
      subuserlib.testImages.testImages(user=user,sourceRepoId=args[0],imageSourceNames=args[1:])
  except subuserlib.portalocker.portalocker.LockException:
    sys.exit("Another subuser process is currently running and has a lock on the registry. Please try again later.")

#################################################################################################

if __name__ == "__main__":
  testImages(sys.argv[1:])

