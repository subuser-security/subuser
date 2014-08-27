#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import optparse
#internal imports
import subuserlib.classes.user

def parseCliArgs():
  usage = "usage: subuser %prog"
  description = """ Remove old, no longer used, installed images.  Note, once you do this, you will no longer be able to return to previous configuration states with subuser update checkout."""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  advancedOptions = subuserlib.commandLineArguments.advancedInstallOptionsGroup(parser)
  parser.add_option_group(advancedOptions)
  return parser.parse_args()

#################################################################################################

parseCliArgs()

user = subuserlib.classes.user.User()

for installedImageId,installedImage in user.getInstalledImages().iteritems():
  imageInUse = False
  for subuser in user.getRegistry().getSubusers():
    if subuser.getImageId() == installedImageId:
      imageInUse = True
  if not imageInUse:
    installedImage.removeDockerImage()

