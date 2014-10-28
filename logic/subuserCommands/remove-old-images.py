#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import pathConfig
#external imports
import optparse,sys
#internal imports
import subuserlib.classes.user,subuserlib.verify,subuserlib.commandLineArguments

def parseCliArgs(realArgs):
  usage = "usage: subuser %prog"
  description = """ Remove old, no longer used, installed images.  Note, once you do this, you will no longer be able to return to previous configuration states with subuser update checkout."""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args(args=realArgs)

def removeOldImages(realArgs):
  """
  Remove images that are installed, but are not associated with any subusers.

  Tests
  -----

  **Setup:**

  >>> remove_old_images = __import__("remove-old-images")#import self
  >>> import subuser
  >>> import subuserlib.classes.user

  Check our assumptions about what subusers are installed in the test environment.  We load a new user object each time we checked, because we are interested about whether the changes we want are present on disk.

  >>> user = subuserlib.classes.user.User()
  >>> set(user.getRegistry().getSubusers().keys()) == set(["foo"])
  True

  Add a ``bar`` subuser, which we will then remove.  This will leave us with a leftover image.

  >>> subuser.subuser(["add","bar","bar@file:///home/travis/remote-test-repo"])
  Adding subuser bar bar@file:///home/travis/remote-test-repo
  Adding new temporary repository file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Installing bar ...
  Installed new image for subuser bar
  Running garbage collector on temporary repositories...

  Check to see if subuser ``bar`` was successfully added.

  >>> user = subuserlib.classes.user.User()
  >>> set(user.getRegistry().getSubusers().keys()) == set([u'foo', 'bar'])
  True

  Check to see if the image for ``bar`` was also installed.

  >>> set([i.getImageSourceName() for i in user.getInstalledImages().values()]) == set([u'foo', u'bar'])
  True

  Remove the ``bar`` subuser.

  >>> subuser.subuser(["remove","bar"])
  Removing subuser bar
   If you wish to remove the subusers image, issue the command $ subuser remove-old-images
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Running garbage collector on temporary repositories...

  See that the image for ``bar`` was indeed left behind.

  >>> user = subuserlib.classes.user.User()
  >>> set([i.getImageSourceName() for i in user.getInstalledImages().values()]) == set([u'foo', u'bar'])
  True

  Now we use ``remove-old-images`` to clean up our installed images.

  >>> remove_old_images.removeOldImages([])
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Running garbage collector on temporary repositories...
  Removing uneeded temporary repository: file:///home/travis/remote-test-repo

  And now the uneccesary ``bar`` image is gone.

  >>> user = subuserlib.classes.user.User()
  >>> set([i.getImageSourceName() for i in user.getInstalledImages().values()]) == set([u'foo'])
  True
 
  """
  parseCliArgs(realArgs)

  user = subuserlib.classes.user.User()

  for installedImageId,installedImage in user.getInstalledImages().items():
    imageInUse = False
    for _,subuser in user.getRegistry().getSubusers().items():
      if subuser.getImageId() == installedImageId:
        imageInUse = True
    if not imageInUse:
      installedImage.removeDockerImage()
  subuserlib.verify.verify(user)
  user.getRegistry().commit()

#################################################################################################

if __name__ == "__main__":
  removeOldImages(sys.argv[1:])

