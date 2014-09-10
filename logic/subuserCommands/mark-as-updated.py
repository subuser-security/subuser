#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
#external modules
import optparse,sys
#internal modules
import subuserlib.installTime,subuserlib.commandLineArguments,subuserlib.resolve,subuserlib.classes.user

def parseCliArgs(sysargs):
  usage = "usage: subuser %prog IMAGE_NAME(s)"
  description = """
Mark a image as needing to be updated.  Note, that this may mess up the formatting of it's permissions.json file.  This command is usefull mainly to the maintainers of subuser.  We use this command when we update a package or hear that it has been updated up stream.  The effect of this command, is that the image will be updated when the user issues `subuser update`. 

EXAMPLE:

$ subuser mark-as-updated firefox@default
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args(args=sysargs[1:])

#################################################################################################

def markAsUpdated(sysargs):
  """
  Mark the given images as needing to be updated by setting their 'last-update-time' attributes to the current time.

  >>> mark_as_updated = __import__("mark-as-updated")#import self
  >>> mark_as_updated.markAsUpdated(["mark-as-updated","foo"])

   Here we test if the updated update time was actually saved correctly.  16 is the length of a standard formatted subuser image update time.

  >>> import subuserlib.classes.user
  >>> user = subuserlib.classes.user.User()
   >>> len(user.getRegistry().getRepositories()["default"]["foo"].getPermissions()["last-update-time"])
   16

  Cleanup:
   >>> import subuserlib.git
   >>> subuserlib.git.runGit(["checkout","HEAD",user.getRegistry().getRepositories()["default"]["foo"].getPermissions().getWritePath()],cwd=user.getRegistry().getRepositories()["default"].getRepoPath())

  If the image doesn't exist, we print a user friendly error message.

  >>> mark_as_updated.markAsUpdated(["mark-as-updated","non-existant-image"])
  Traceback (most recent call last):
  SystemExit: Could not mark the image: non-existant-image as needing an update.  Image does not exist.
  """
  user=subuserlib.classes.user.User()
  options,imageIds = parseCliArgs(sysargs)

  for imageId in imageIds:
    try:
      image = subuserlib.resolve.resolveImageSource(user,imageId)
      image.getPermissions()["last-update-time"] = subuserlib.installTime.currentTimeString()
      image.getPermissions().save()
    except KeyError:
      sys.exit("Could not mark the image: "+imageId+" as needing an update.  Image does not exist.")

if __name__ == "__main__":
  markAsUpdated(sys.argv)
