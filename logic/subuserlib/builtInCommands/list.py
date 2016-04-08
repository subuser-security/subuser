#!/usr/bin/python3
# -*- coding: utf-8 -*-
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
import subuserlib.print

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
def runCommand(sysargs):
  """
  List various things: image sources, subusers, ect.
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
    availableDict = {}
    for repoIdentifier in reposToList:
      try:
        repoIdentifier = repoIdentifier.decode("utf-8")
      except AttributeError:
        pass
      if repoIdentifier in user.getRegistry().getRepositories():
        temp = False
      else:
        temp = True
      try:
        repository = subuserlib.resolve.resolveRepository(user,repoIdentifier)
      except (OSError,subuserlib.resolve.ResolutionError):
        sys.exit("Repository id: "+repoIdentifier+" could not be resolved.")
      if options.json:
        availableDict[repository.getName()] = repository.serializeToDict()
      else:
       if options.long:
         subuserlib.print.printWithoutCrashing("Images available for instalation from the repo: " + repository.getName())
       for imageSource in repository.getSortedList():
         if not options.long:
           identifier = imageSource.getIdentifier()
           subuserlib.print.printWithoutCrashing(identifier)
         else:
           try:
             imageSource.describe()
           except SyntaxError as e:
             subuserlib.print.printWithoutCrashing(str(e))
             subuserlib.print.printWithoutCrashing("Cannot describe this image source as loading it is forbidden.")
      if temp:
        repository.removeGitRepo()
    if options.json:
      subuserlib.print.printWithoutCrashing(json.dumps(availableDict,indent=1,separators=(",",": ")))
    sys.exit()
  elif args[0] == 'subusers':
    if options.json:
      subuserlib.print.printWithoutCrashing(json.dumps(user.getRegistry().getSubusers().serializeToDict(),indent=1,separators=(",",": ")))
      sys.exit()
    if options.long:
      subuserlib.print.printWithoutCrashing("The following subusers are registered.")
    for name,subuser in user.getRegistry().getSubusers().items():
      if options.internal or not name.startswith("!"):
        if not options.long:
          subuserlib.print.printWithoutCrashing(name)
        else:
          subuser.describe()
  elif args[0] == 'installed-images':
    if options.json:
      subuserlib.print.printWithoutCrashing(json.dumps(user.getInstalledImages().serializeToDict(),indent=1,separators=(",",": ")))
      sys.exit()
    if options.long:
      subuserlib.print.printWithoutCrashing("The following images are installed.")
    for id,installedImage in user.getInstalledImages().items():
      if not options.long:
        try:
          identifier = installedImage.getImageSource().getIdentifier()
          if not options.broken:
            subuserlib.print.printWithoutCrashing(identifier+" "+id)
        except KeyError:
          if options.broken:
            subuserlib.print.printWithoutCrashing(id)
      else:
        subuserlib.print.printWithoutCrashing("------------------")
        installedImage.describe()
  elif args[0] == 'repositories':
    if options.json:
      subuserlib.print.printWithoutCrashing(json.dumps(user.getRegistry().getRepositories().serializeToDict(),indent=1,separators=(",",": ")))
      sys.exit()
    for name,repo in user.getRegistry().getRepositories().items():
      if not options.long:
        subuserlib.print.printWithoutCrashing(repo.getDisplayName())
      else:
        repo.describe()
        subuserlib.print.printWithoutCrashing("")
  else:
    sys.exit(args[0] + " cannot be listed. Option unrecognized. Use --help for help.")
