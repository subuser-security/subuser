#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import optparse,sys
#internal imports
import subuserlib.classes.user,subuserlib.commandLineArguments,subuserlib.resolve

def parseCliArgs(sysargs):
  usage = "usage: subuser %prog describe [subuser|program] SUBUSER(s)/PROGRAM(s)"
  description = """Show basic information about a subuser or program: Whether it is installed, what it's permissions are ect.
Ex:
$ subuser describe program firefox
<lots of info>
$ subuser describe program firefox
"""
  parser = optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args(args=sysargs[2:])

def describe(sysargs):
  """
  Describe subusers and programs.
  
  >>> import describe #import self
  >>> describe.describe([sys.argv[0]]+["describe","subuser","foo"])
  Subuser: foo
  ------------------
  Progam:
  foo:
   Description: 
   Maintainer: 
   Last update time(version): 0
   Executable: /usr/bin/foo
  >>> describe.describe([sys.argv[0]]+["describe","program","foo"])
  foo:
   Description: 
   Maintainer: 
   Last update time(version): 0
   Executable: /usr/bin/foo
  >>> describe.describe([sys.argv[0]]+["describe","program","foo@default"])
  foo:
   Description: 
   Maintainer: 
   Last update time(version): 0
   Executable: /usr/bin/foo
  """
  user = subuserlib.classes.user.User()
  (options,args) = parseCliArgs(sysargs)
  if args[0] == "program":
    for program in args[1:]:
      subuserlib.resolve.resolveProgramSource(user,program).describe()
  elif args[0] == "subuser":
    for subuser in  args[1:]:
      user.getRegistry().getSubusers()[subuser].describe()
  #else:
    #parseCliArgs(["","subuser","describe","--help"])

if __name__ == "__main__":
  describe(sys.argv)
