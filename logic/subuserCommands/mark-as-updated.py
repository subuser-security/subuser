#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
#external modules
import optparse,sys
#internal modules
import subuserlib.installTime,subuserlib.commandLineArguments,subuserlib.classes.permissions,subuserlib.classes.user

def parseCliArgs(sysargs):
  usage = "usage: subuser %prog permissions.json_file(s)"
  description = """
Mark a image as needing to be updated.  Note, that this may mess up the formatting of it's permissions.json file.  This command is usefull mainly to the maintainers of subuser.  We use this command when we update a package or hear that it has been updated up stream.  The effect of this command, is that the image will be updated when the user issues `subuser update`. 

EXAMPLE:

    $ subuser mark-as-updated firefox/permissions.json 
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args(args=sysargs[1:])

#################################################################################################

def markAsUpdated(sysargs):
  """
  Mark the given images as needing to be updated by setting their 'last-update-time' attributes to the current time.

  >>> mark_as_updated = __import__("mark-as-updated")#import self, os
  >>> import subuserlib.classes.user,os
  >>> user = subuserlib.classes.user.User()
  >>> foosPermissionsFilePath = os.path.join(user.getRegistry().getRepositories()["default"]["foo"].getSourceDir(),"permissions.json")
  >>> mark_as_updated.markAsUpdated(["mark-as-updated",foosPermissionsFilePath])

   Here we test if the updated update time was actually saved correctly.  16 is the length of a standard formatted subuser image update time.

   >>> len(user.getRegistry().getRepositories()["default"]["foo"].getPermissions()["last-update-time"])
   16

  Cleanup:
   >>> import subuserlib.git
   >>> subuserlib.git.runGit(["checkout","HEAD",user.getRegistry().getRepositories()["default"]["foo"].getPermissions().getWritePath()],cwd=user.getRegistry().getRepositories()["default"].getRepoPath())

  If the file doesn't exist, we print a user friendly error message.

  >>> mark_as_updated.markAsUpdated(["mark-as-updated","/non-existant-path/permissions.json"])
  Traceback (most recent call last):
  SystemExit: Could not mark the file /non-existant-path/permissions.json as needing an update.  File does not exist.
  """
  user=subuserlib.classes.user.User()
  options,permissionsFiles = parseCliArgs(sysargs)

  for permissionsFile in permissionsFiles:
    try:
      permissions = subuserlib.classes.permissions.Permissions(user,readPath=permissionsFile,writePath=permissionsFile)
      permissions["last-update-time"] = subuserlib.installTime.currentTimeString()
      permissions.save()
    except IOError:
      sys.exit("Could not mark the file "+permissionsFile+" as needing an update.  File does not exist.")

if __name__ == "__main__":
  markAsUpdated(sys.argv)
