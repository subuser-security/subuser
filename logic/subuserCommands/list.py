#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import sys,os,optparse
#internal imports
import subuserlib.classes.user,subuserlib.commandLineArguments

def parseCliArgs(sysargs):
  usage = "usage: subuser %prog WHAT_TO_LIST [options]"
  description = """   List subuser-images.  You can use this command to list images that are:

  available 
      List all subuser images available for instalation
  subusers 
      List all installed subusers

  EXAMPLES:
    $ subuser list available --short
    $ subuser list subusers
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--short",dest="short",action="store_true",default=False,help="Only display the names of the images to be listed, and no other information.")
  return parser.parse_args(args=sysargs[1:])

#################################################################################################

def list(sysargs):
  """
  List various things: image sources, subusers, ect.

  >>> import sys
  >>> import list #import self
  >>> list.list([sys.argv[0]]+["list","available"])
  Images available for instalation from the repo: default
  foo:
   Description: 
   Maintainer: 
   Last update time(version): 0
   Executable: /usr/bin/foo
  >>> list.list([sys.argv[0]]+["list","subusers"])
  The following subusers are registered.
  Subuser: foo
  ------------------
  Progam:
  foo:
   Description: 
   Maintainer: 
   Last update time(version): 0
   Executable: /usr/bin/foo
  """
  options,args = parseCliArgs(sysargs)
  
  if len(args)==0:
    sys.exit("Nothing to list. Issue this command with the -h argument for help.")
  
  user = subuserlib.classes.user.User()
  
  if 'available' in args:
    for repoName,repository in user.getRegistry().getRepositories().iteritems():
      print("Images available for instalation from the repo: " + repoName)
      for imageName,imageSource in repository.iteritems():
        imageSource.describe()
  
  if 'subusers' in args:
    print("The following subusers are registered.")
    for name,subuser in user.getRegistry().getSubusers().iteritems():
      subuser.describe()

if __name__ == "__main__":
  list(sys.argv)
