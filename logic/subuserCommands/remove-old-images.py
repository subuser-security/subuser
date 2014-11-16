#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import pathConfig
#external imports
import optparse,sys
#internal imports
import subuserlib.classes.user,subuserlib.commandLineArguments,subuserlib.removeOldImages

def parseCliArgs(realArgs):
  usage = "usage: subuser %prog"
  description = """ Remove old, no longer used, installed images.  Note, once you do this, you will no longer be able to return to previous configuration states with subuser update checkout."""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--dry-run", dest="dryrun",action="store_true",default=False,help="Don't actually delete the images. Print which images would be deleted.")
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

  Use dry-run to see which images are to be deleted.

  >>> remove_old_images.removeOldImages(["--dry-run"])
  The following images are uneeded and would be deleted.
  DOCKER-ID : SUBUSER-ID
  5 : bar@file:///home/travis/remote-test-repo

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
  options,args = parseCliArgs(realArgs)

  user = subuserlib.classes.user.User()

  if options.dryrun:
    print("The following images are uneeded and would be deleted.")
    print("DOCKER-ID : SUBUSER-ID")

  subuserlib.removeOldImages.removeOldImages(user=user,dryrun=options.dryrun)

#################################################################################################

if __name__ == "__main__":
  removeOldImages(sys.argv[1:])

