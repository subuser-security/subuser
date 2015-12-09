#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

try:
  import pathConfig
except ImportError:
  pass
#external imports
import sys
import os
import optparse
import json
#internal imports
import subuserlib.classes.user
import subuserlib.commandLineArguments
import subuserlib.resolve
import subuserlib.profile

def parseCliArgs(sysargs):
  usage = "usage: subuser list WHAT_TO_LIST [options]"
  description = """   List subuser-images.  You can use this command to list images that are:

  available
      List all subuser images available for instalation
  subusers
      List all installed subusers
  installed-images
      List all installed images. The the format is "<image-source> <image-id>". If the --long option is used, then information about each image is displayed.
  repositories
      List all repositories. By default, lists repository names(or their paths in case they are temporary). With the --long option, more info about each repository is printed.

  EXAMPLES:

    $ subuser list available --long
    $ subuser list subusers
    $ subuser list installed-images
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--long",dest="long",action="store_true",default=False,help="Display more information about each item.")
  parser.add_option("--json",dest="json",action="store_true",default=False,help="Display results in JSON format.")
  parser.add_option("--internal",dest="internal",action="store_true",default=False,help="Include internal subusers in the list. These are subusers which are automatically created and used by subuser internally.")
  parser.add_option("--broken",dest="broken",action="store_true",default=False,help="When listing installed images option, list the Ids of broken/orphaned images. Otherwise has no effect. Without this option, broken/orphaned images are simply not listed.")
  return parser.parse_args(args=sysargs)

#################################################################################################

@subuserlib.profile.do_cprofile
def list(sysargs):
  """
  List various things: image sources, subusers, ect.

  >>> import sys
  >>> list = __import__("subuser-list") #import self

  Listing available images lists the images along with their default permissions.

  >>> list.list(["available"])
  foo@default

  Similar result when listing subusers.

  >>> list.list(["subusers"])
  foo

  And listing installed images:

  >>> list.list(["installed-images"])
  foo@default 2

  > list.list(["repositories"])
  foo

  In all cases, there is a ``--long`` option. (We don't test this, because the hash changes every time.)

  >> list.list(["repositories","--long"])
  Repository: default
  ------------
  Cloned from: file:///home/travis/default-test-repo
  Currently at commit: 7ef30a4e1267f9f026e3be064f120290c28ef29e
  <BLANKLINE>

  >>> list.list(["subusers","--long"])
  The following subusers are registered.
  Subuser: foo
  ------------------
  foo@default
   Description:
   Maintainer:
   Executable: /usr/bin/foo
  <BLANKLINE>

  >>> list.list(["available","--long"])
  Images available for instalation from the repo: default
  foo@default
   Description:
   Maintainer:
   Executable: /usr/bin/foo

  You can specify which repository to list image sources from.

  >>> list.list(["available","default","--long"])
  Images available for instalation from the repo: default
  foo@default
   Description:
   Maintainer:
   Executable: /usr/bin/foo

  When listing available image sources, refering to a repository via a URI works as well.

  >>> list.list(["available","file:///home/travis/version-constrained-test-repo"])
  Adding new temporary repository file:///home/travis/version-constrained-test-repo
  bop@file:///home/travis/version-constrained-test-repo

  >>> list.list(["installed-images"])
  foo@default 2

  >>> list.list(["repositories"])
  default

  """
  options,args = parseCliArgs(sysargs)
  if len(args)==0:
    sys.exit("Nothing to list. Issue this command with the -h argument for help.")
  user = subuserlib.classes.user.User()
  if args[0] == 'available':
    if len(args) > 1:
      reposToList = args[1:]
    else:
      reposToList = user.getRegistry().getRepositories().keys()
    if options.json:
      availableDict = {}
      for repoIdentifier in reposToList:
        if repoIdentifier in user.getRegistry().getRepositories():
          temp = False
        else:
          temp = True
        repository = subuserlib.resolve.resolveRepository(user,repoIdentifier)
        availableDict[repository.getName()] = repository.serializeToDict()
        if temp:
          repository.removeGitRepo()
      print(json.dumps(availableDict,indent=1,separators=(",",": ")))
      sys.exit()
    for repoIdentifier in reposToList:
      if repoIdentifier in user.getRegistry().getRepositories():
        temp = False
      else:
        temp = True
      repository =  subuserlib.resolve.resolveRepository(user,repoIdentifier)
      if options.long:
        print("Images available for instalation from the repo: " + repository.getName())
      for _,imageSource in repository.items():
        if not options.long:
          print(imageSource.getIdentifier())
        else:
          imageSource.describe()
      if temp:
        repository.removeGitRepo()
  elif args[0] == 'subusers':
    if options.json:
      print(json.dumps(user.getRegistry().getSubusers().serializeToDict(),indent=1,separators=(",",": ")))
      sys.exit()
    if options.long:
      print("The following subusers are registered.")
    for name,subuser in user.getRegistry().getSubusers().items():
      if options.internal or not name.startswith("!"):
        if not options.long:
          print(name)
        else:
          subuser.describe()
  elif args[0] == 'installed-images':
    if options.json:
      print(json.dumps(user.getInstalledImages().serializeToDict(),indent=1,separators=(",",": ")))
      sys.exit()
    if options.long:
      print("The following images are installed.")
    for id,installedImage in user.getInstalledImages().items():
      if not options.long:
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
  elif args[0] == 'repositories':
    if options.json:
      print(json.dumps(user.getRegistry().getRepositories().serializeToDict(),indent=1,separators=(",",": ")))
      sys.exit()
    for name,repo in user.getRegistry().getRepositories().items():
      if not options.long:
        print(repo.getDisplayName())
      else:
        repo.describe()
        print("")
  else:
    sys.exit(args[0] + " cannot be listed. Option unrecognized.")

if __name__ == "__main__":
  list(sys.argv[1:])
