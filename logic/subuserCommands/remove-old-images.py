#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import pathConfig
#external imports
import sys
import optparse
#internal imports
from subuserlib.classes.user import User
import subuserlib.commandLineArguments
import subuserlib.removeOldImages

def parseCliArgs(realArgs):
  usage = "usage: subuser %prog"
  description = """ Remove old, no longer used, installed images.  Note, once you do this, you will no longer be able to return to previous configuration states with subuser update checkout."""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--dry-run", dest="dryrun",action="store_true",default=False,help="Don't actually delete the images. Print which images would be deleted.")
  parser.add_option("--repo", dest="repo",default=None,help="Only remove images from the given repository.")
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

  >>> user = User()
  >>> subuserList = list(user.getRegistry().getSubusers().keys())
  >>> subuserList.sort()
  >>> for sb in subuserList:
  ...   print(sb)
  foo

  Add a ``bar`` subuser, which we will then remove.  This will leave us with a leftover image.

  >>> subuser.subuser(["add","--accept","bar","bar@file:///home/travis/remote-test-repo"])
  Adding subuser bar bar@file:///home/travis/remote-test-repo
  Adding new temporary repository file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  bar would like to have the following permissions:
   Description: 
   Maintainer: 
   Executable: /usr/bin/bar
  A - Accept and apply changes
  E - Apply changes and edit result
  A
  Checking if images need to be updated or installed...
  Checking if subuser bar is up to date.
  Installing bar ...
  Building...
  Building...
  Building...
  Successfully built 5
  Building...
  Building...
  Building...
  Successfully built 6
  Installed new image <6> for subuser bar
  Running garbage collector on temporary repositories...

  Check to see if subuser ``bar`` was successfully added.

  >>> user = User()
  >>> subuserList = list(user.getRegistry().getSubusers().keys())
  >>> subuserList.sort()
  >>> for sb in subuserList:
  ...   print(sb)
  bar
  foo

  Check to see if the image for ``bar`` was also installed.

  >>> installedImages = list([i.getImageSourceName() for i in user.getInstalledImages().values()])
  >>> installedImages.sort()
  >>> for installedImage in installedImages:
  ...   print(installedImage)
  bar
  foo

  Remove the ``bar`` subuser.

  >>> subuser.subuser(["remove","bar"])
  Removing subuser bar
   If you wish to remove the subusers image, issue the command $ subuser remove-old-images
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Running garbage collector on temporary repositories...

  See that the image for ``bar`` was indeed left behind.

  >>> user = User()
  >>> installedImages = list([i.getImageSourceName() for i in user.getInstalledImages().values()])
  >>> installedImages.sort()
  >>> for installedImage in installedImages:
  ...   print(installedImage)
  bar
  foo

  Use dry-run to see which images are to be deleted.

  >>> remove_old_images.removeOldImages(["--dry-run"])
  The following images are uneeded and would be deleted.
  DOCKER-ID : SUBUSER-ID
  Removing unneeded image 6 : bar@file:///home/travis/remote-test-repo

  Check to see that dry-run didn't actually remove the un-needed image.

  >>> user = User()
  >>> installedImages = list([i.getImageSourceName() for i in user.getInstalledImages().values()])
  >>> installedImages.sort()
  >>> for installedImage in installedImages:
  ...   print(installedImage)
  bar
  foo

  Add another subuser blah

  >>> subuser.subuser(["add","--accept","blah","blah@/home/travis/local-test-repo"])
  Adding subuser blah blah@/home/travis/local-test-repo
  Adding new temporary repository /home/travis/local-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  blah would like to have the following permissions:
   Description: 
   Maintainer: 
   Executable: /usr/bin/foo
  A - Accept and apply changes
  E - Apply changes and edit result
  A
  Checking if images need to be updated or installed...
  Checking if subuser blah is up to date.
  Installing blah ...
  Building...
  Building...
  Building...
  Successfully built 8
  Building...
  Building...
  Building...
  Successfully built 9
  Installed new image <9> for subuser blah
  Running garbage collector on temporary repositories...

  Check to see if subuser ``blah`` was successfully added.

  >>> user = User()
  >>> subuserList = list(user.getRegistry().getSubusers().keys())
  >>> subuserList.sort()
  >>> for sb in subuserList:
  ...   print(sb)
  blah
  foo

  Check to see if the image for ``blah`` was also installed.

  >>> installedImageList = list([i.getImageSourceName() for i in user.getInstalledImages().values()])
  >>> installedImageList.sort()
  >>> for installedImage in installedImageList:
  ...   print(installedImage)
  bar
  blah
  foo

  Remove the ``blah`` subuser.

  >>> subuser.subuser(["remove","blah"])
  Removing subuser blah
   If you wish to remove the subusers image, issue the command $ subuser remove-old-images
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Running garbage collector on temporary repositories...

  See that the image for ``blah`` was indeed left behind.

  >>> user = User()
  >>> installedImageList = list([i.getImageSourceName() for i in user.getInstalledImages().values()])
  >>> installedImageList.sort()
  >>> for installedImage in installedImageList:
  ...   print(installedImage)
  bar
  blah
  foo

  Now we use ``remove-old-images`` to remove images which belong to the local repository.

  >>> remove_old_images.removeOldImages(["--repo=/home/travis/local-test-repo"])
  Removing unneeded image 9 : blah@/home/travis/local-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Running garbage collector on temporary repositories...
  Removing uneeded temporary repository: /home/travis/local-test-repo

  Now we use ``remove-old-images`` to clean up the rest of our un-needed installed images.

  >>> remove_old_images.removeOldImages([])
  Removing unneeded image 6 : bar@file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Running garbage collector on temporary repositories...
  Removing uneeded temporary repository: file:///home/travis/remote-test-repo

  And now the uneccesary ``bar`` image is gone.

  >>> user = User()
  >>> installedImages = list([i.getImageSourceName() for i in user.getInstalledImages().values()])
  >>> installedImages.sort()
  >>> for installedImage in installedImages:
  ...   print(installedImage)
  foo
 
  """
  options,args = parseCliArgs(realArgs)
  user = User()
  try:
    with user.getRegistry().getLock() as lockFileHandler:
      if options.dryrun:
        print("The following images are uneeded and would be deleted.")
        print("DOCKER-ID : SUBUSER-ID")
      repoId = options.repo
      if not repoId is None:
        if not repoId in user.getRegistry().getRepositories():
          repo = subuserlib.resolve.lookupRepositoryByURI(user,options.repo)
          if repo is None:
            sys.exit("The repository <"+repoId+"> does not exist.")
          else:
            repoId = repo.getName()
      subuserlib.removeOldImages.removeOldImages(user=user,dryrun=options.dryrun,sourceRepoId=repoId)
  except subuserlib.portalocker.portalocker.LockException:
    sys.exit("Another subuser process is currently running and has a lock on the registry. Please try again later.")

#################################################################################################

if __name__ == "__main__":
  removeOldImages(sys.argv[1:])
