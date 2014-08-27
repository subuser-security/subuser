#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
#external modules
import optparse,sys
#internal modules
import subuserlib.installTime,subuserlib.commandLineArguments,subuserlib.resolve,subuserlib.classes.user

def parseCliArgs(sysargs):
  usage = "usage: subuser %prog PROGRAM_NAME(s)"
  description = """
Mark a program as needing to be updated.  Note, that this may mess up the formatting of it's permissions.json file.  This command is usefull mainly to the maintainers of subuser.  We use this command when we update a package or hear that it has been updated up stream.  The effect of this command, is that the program will be updated when the user issues `subuser update`. 

EXAMPLE:

$ subuser mark-as-updated firefox@default
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args(args=sysargs[2:])

#################################################################################################

def markAsUpdated(sysargs):
  """
  Mark the given programs as needing to be updated by setting their 'last-update-time' attributes to the current time.

  >>> mark_as_updated = __import__("mark-as-updated")#import self
  >>> mark_as_updated.markAsUpdated([sys.argv[0]]+["mark-as-updated","foo"])

   Here we test if the updated update time was actually saved correctly.  16 is the length of a standard formatted subuser program update time.

  >>> import subuserlib.classes.user
  >>> user = subuserlib.classes.user.User()
   >>> len(user.getRegistry().getRepositories()["default"]["foo"].getPermissions()["last-update-time"])
   16

  If the program doesn't exist, we print a user friendly error message.

  >>> mark_as_updated.markAsUpdated([sys.argv[0]]+["mark-as-updated","non-existant-program"])
  Traceback (most recent call last):
  SystemExit: Could not mark the program: non-existant-program as needing an update.  Program does not exist.
  """
  user=subuserlib.classes.user.User()
  options,programIds = parseCliArgs(sysargs)

  for programId in programIds:
    try:
      program = subuserlib.resolve.resolveProgramSource(user,programId)
      program.getPermissions()["last-update-time"] = subuserlib.installTime.currentTimeString()
      program.getPermissions().save()
    except KeyError:
      sys.exit("Could not mark the program: "+programId+" as needing an update.  Program does not exist.")

if __name__ == "__main__":
  markAsUpdated(sys.argv)
