#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import optparse
#internal imports
import subuserlib.classes.user,subuserlib.verify,subuserlib.commandLineArguments

def parseCliArgs():
  usage = "usage: subuser %prog"
  description = """ Remove old, no longer used, installed images.  Note, once you do this, you will no longer be able to return to previous configuration states with subuser update checkout."""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args()

def removeOldImages(user):
  """
  Remove images that are installed, but are not associated with any subusers.

 >>> remove_old_images = __import__("remove-old-images")#import self
 >>> import subuserlib.classes.user,subuserlib.subuser
 >>> user = subuserlib.classes.user.User()
 >>> user.getRegistry().getSubusers().keys()
 [u'foo']
 >>> subuserlib.subuser.add(user,"bar","bar@file:///home/travis/remote-test-repo")
 Adding new temporary repository file:///home/travis/remote-test-repo
 Adding subuser bar bar@file:///home/travis/remote-test-repo
 Verifying subuser configuration.
 Verifying registry consistency...
 Unregistering any non-existant installed images.
 Checking if images need to be updated or installed...
 Installing bar ...
 Installed new image for subuser bar
 Running garbage collector on temporary repositories...
 >>> user.getRegistry().getSubusers().keys()
 [u'foo', 'bar']
 >>> [i.getImageSourceName() for i in user.getInstalledImages().values()]
 [u'foo', u'bar']
 >>> subuserlib.subuser.remove(user,"bar")
 Removing subuser bar
  If you wish to remove the subusers image, issue the command $ subuser remove-old-images
 Verifying subuser configuration.
 Verifying registry consistency...
 Unregistering any non-existant installed images.
 Checking if images need to be updated or installed...
 Running garbage collector on temporary repositories...
 >>> [i.getImageSourceName() for i in user.getInstalledImages().values()]
 [u'foo', u'bar']
 >>> remove_old_images.removeOldImages(user)
 Verifying subuser configuration.
 Verifying registry consistency...
 Unregistering any non-existant installed images.
 Checking if images need to be updated or installed...
 Running garbage collector on temporary repositories...
 Removing uneeded temporary repository: file:///home/travis/remote-test-repo
 >>> [i.getImageSourceName() for i in user.getInstalledImages().values()]
 [u'foo']
  """
  for installedImageId,installedImage in user.getInstalledImages().iteritems():
    imageInUse = False
    for _,subuser in user.getRegistry().getSubusers().iteritems():
      if subuser.getImageId() == installedImageId:
        imageInUse = True
    if not imageInUse:
      installedImage.removeDockerImage()
  subuserlib.verify.verify(user)
  user.getRegistry().commit()

#################################################################################################


if __name__ == "__main__":
  parseCliArgs()
  user = subuserlib.classes.user.User()
  removeOldImages(user)

