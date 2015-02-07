#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import pathConfig
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
  installed-images
      List all installed images. The --short option prints with the format "<image-source> <image-id>"

  EXAMPLES:

    $ subuser list available --short
    $ subuser list subusers
    $ subuser list installed-images
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--short",dest="short",action="store_true",default=False,help="Only display the names of the images to be listed, and no other information.")
  parser.add_option("--broken",dest="broken",action="store_true",default=False,help="When listing installed images with the --short option, list the Ids of broken/orphaned images. Otherwise has no effect. Without this option, broken/orphaned images are simply not listed in the --short mode.")
  return parser.parse_args(args=sysargs)

#################################################################################################

def list(sysargs):
  """
  List various things: image sources, subusers, ect.

  >>> import sys
  >>> import list #import self

  Listing available images lists the images along with their default permissions.

  >>> list.list(["available"])
  Images available for instalation from the repo: default
  foo:
   Description: 
   Maintainer: 
   Last update time(version): 0
   Executable: /usr/bin/foo

  Similar result when listing subusers.

  >>> list.list(["subusers"])
  The following subusers are registered.
  Subuser: foo
  ------------------
  Progam:
  foo:
   Description: 
   Maintainer: 
   Last update time(version): 0
   Executable: /usr/bin/foo

  And listing installed images:

  >>> list.list(["installed-images"])
  The following images are installed.
  ------------------
  Image Id: 2
  Image source: foo@default
  Last update time: 0

  In all cases, there is a ``--short`` option.

  >>> list.list(["subusers","--short"])
  foo

  >>> list.list(["available","--short"])
  foo@default

  >>> list.list(["installed-images","--short"])
  foo@default 2

  """
  options,args = parseCliArgs(sysargs)
 
  if len(args)==0:
    sys.exit("Nothing to list. Issue this command with the -h argument for help.")
  
  user = subuserlib.classes.user.User()
  
  if 'available' in args:
    for repoName,repository in user.getRegistry().getRepositories().items():
      if not options.short:
        print("Images available for instalation from the repo: " + repoName)
      for _,imageSource in repository.items():
        if options.short:
          print(imageSource.getIdentifier())
        else:
          imageSource.describe()
  
  if 'subusers' in args:
    if not options.short:
      print("The following subusers are registered.")
    for name,subuser in user.getRegistry().getSubusers().items():
      if options.short:
        print(name)
      else:
        subuser.describe()

  if 'installed-images' in args:
    if not options.short:
      print("The following images are installed.")
    for id,installedImage in user.getInstalledImages().items():
      if options.short:
        try:
          identifier = installedImage.getImageSource().getIdentifier()
          if not options.broken:
            print(identifier+" "+id)
        except KeyError:
          if options.broken:
            print(id)
      else:
        print("------------------")
        installedImage.describe()

if __name__ == "__main__":
  list(sys.argv[1:])
