#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import optparse
#internal imports
import subuserlib.classes.user,subuserlib.verify

def parseCliArgs():
  usage = "usage: subuser %prog"
  description = """ Remove old, no longer used, installed images.  Note, once you do this, you will no longer be able to return to previous configuration states with subuser update checkout."""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  advancedOptions = subuserlib.commandLineArguments.advancedInstallOptionsGroup(parser)
  parser.add_option_group(advancedOptions)
  return parser.parse_args()

def removeOldImages(user):
  """
  Remove images that are installed, but are not associated with any subusers.

 >>> remove_old_images = __import__("remove-old-images")#import self
 >>> import subuserlib.classes.user,subuserlib.subuser
 >>> user = subuserlib.classes.user.User()
 >>> subuserlib.subuser.add(user,"bar","bar@file:///home/travis/remote-test-repo")
 Adding new temporary repository file:///home/travis/remote-test-repo
 Adding subuser bar bar@file:///home/travis/remote-test-repo
 Verifying subuser configuration.
 Verifying registry consistency...
 Checking if images need to be updated or installed...
 Installing foo ...
 Installed new image for subuser foo
 Installing bar ...
 Installed new image for subuser bar
 Running garbage collector on temporary repositories...
 >>> user.getInstalledImages().keys()
 [u'1', '2']
 >>> subuserlib.subuser.remove(user,"bar")
 Removing subuser bar
 Verifying subuser configuration.
 Verifying registry consistency...
 Checking if images need to be updated or installed...
 Running garbage collector on temporary repositories...
 >>> user.getInstalledImages().keys()
 [u'1', '2']
 >>> remove_old_images.removeOldImages(user)
 Verifying subuser configuration.
 Verifying registry consistency...
 Checking if images need to be updated or installed...
 Running garbage collector on temporary repositories...
 Removing uneeded temporary repository: file:///home/travis/remote-test-repo
 >>> user.getInstalledImages().keys()
 [u'1']
  """
  for installedImageId,installedImage in user.getInstalledImages().iteritems():
    imageInUse = False
    for _,subuser in user.getRegistry().getSubusers().iteritems():
      if subuser.getImageId() == installedImageId:
        imageInUse = True
    if not imageInUse:
      installedImage.removeDockerImage()
  subuserlib.verify.verify(user)

#################################################################################################


if __name__ == "__main__":
  parseCliArgs()
  user = subuserlib.classes.user.User()
  removeOldImages(user)

