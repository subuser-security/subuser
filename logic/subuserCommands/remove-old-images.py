#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import pathConfig
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

  Tests
  -----

  **Setup:**

  >>> remove_old_images = __import__("remove-old-images")#import self
  >>> import subuserlib.classes.user,subuserlib.subuser
  >>> user = subuserlib.classes.user.User()

  Check our assumptions about what subusers are installed in the test environment.

  >>> user.getRegistry().getSubusers().keys()
  [u'foo']

  Add a ``bar`` subuser, which we will then remove.  This will leave us with a leftover image.

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

  Check to see if subuser ``bar`` was successfully added.

  >>> user.getRegistry().getSubusers().keys()
  [u'foo', 'bar']

  Check to see if the image for ``bar`` was also installed.

  >>> [i.getImageSourceName() for i in user.getInstalledImages().values()]
  [u'foo', u'bar']

  Remove the ``bar`` subuser.

  >>> subuserlib.subuser.remove(user,"bar")
  Removing subuser bar
   If you wish to remove the subusers image, issue the command $ subuser remove-old-images
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Running garbage collector on temporary repositories...

  See that the image for ``bar`` was indeed left behind.

  >>> [i.getImageSourceName() for i in user.getInstalledImages().values()]
  [u'foo', u'bar']

  Now we use ``remove-old-images`` to clean up our installed images.

  >>> remove_old_images.removeOldImages(user)
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Running garbage collector on temporary repositories...
  Removing uneeded temporary repository: file:///home/travis/remote-test-repo

  And now the uneccesary ``bar`` image is gone.

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

