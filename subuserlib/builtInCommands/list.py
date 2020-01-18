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
  subuser <subuser-name>
      Describe a given subuser
  installed-images
      List all installed images. The the format is "<image-source> <image-id>". If the --long option is used, then information about each image is displayed.
  image <image-identifier>
      Describe a given image.
  repositories
      List all repositories. By default, lists repository names(or their paths in case they are temporary). With the --long option, more info about each repository is printed.

  EXAMPLES:

    $ subuser list subusers
    $ subuser list subusers <subuser-name> <another-subuser-name>
    $ subuser list available --long
    $ subuser list available <repo-name> <another-repo-name>
    $ subuser list image <image-id> <another-image-id>
    $ subuser list installed-images
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--long",dest="long",action="store_true",default=False,help="Display more information about each item.")
  parser.add_option("--json",dest="json",action="store_true",default=False,help="Display results in JSON format.")
  parser.add_option("--rst",dest="rst",action="store_true",default=False,help="Display results in RestructuredText format.")
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
    reposToList = args[1:] if len(args) > 1 else user.registry.repositories.keys()
    availableDict = {}
    for repoIdentifier in reposToList:
      try:
        repoIdentifier = repoIdentifier.decode("utf-8")
      except AttributeError:
        pass
      temp = not repoIdentifier in user.registry.repositories
      try:
        repository = subuserlib.resolve.resolveRepository(user,repoIdentifier)
      except subuserlib.resolve.ResolutionError as e:
        sys.exit("Repository id: "+repoIdentifier+" could not be resolved.\n" + str(e))
      if options.json:
        availableDict[repository.displayName] = repository.serializeToDict()
      else:
       if options.long:
         if options.rst:
           subuserlib.print.printWithoutCrashing(repository.displayName + "\n"+"="*len(repository.displayName)+"\n")
         else:
           subuserlib.print.printWithoutCrashing("Images available for instalation from the repo: " + repository.displayName)
       for imageSource in repository.getSortedList():
         if not options.long:
           identifier = imageSource.getIdentifier()
           prefix = ""
           if options.rst:
             prefix = " - "
           subuserlib.print.printWithoutCrashing(prefix + identifier)
         else:
           try:
             imageSource.describe(rst=options.rst)
             subuserlib.print.printWithoutCrashing("")
           except SyntaxError as e:
             subuserlib.print.printWithoutCrashing(str(e))
             subuserlib.print.printWithoutCrashing("Cannot describe this image source as loading it is forbidden.")
      if temp:
        repository.removeGitRepo()
    if options.json:
      subuserlib.print.printWithoutCrashing(json.dumps(availableDict,indent=1,separators=(",",": ")))
    sys.exit()

  elif args[0] == 'subusers' or args[0] == 'subuser':
    if args[0] == 'subuser':
      options.long = True
    if len(args) > 1:
      subusersToList = args[1:]
    else:
      subusersToList = user.registry.subusers.keys()
    if options.json:
      subusersDict = user.registry.subusers.serializeToDict()
      toBeShownDict = {}
      for name in subusersToList:
        try:
          toBeShownDict[name] = subusersDict["unlocked"][name]
        except KeyError:
          try:
            toBeShownDict[name] = subusersDict["locked"][name]
          except KeyError:
            sys.exit("Subuser "+name+" does not exist.")
      subuserlib.print.printWithoutCrashing(json.dumps(toBeShownDict,indent=1,separators=(",",": ")))
      sys.exit()
    if options.long:
      subuserlib.print.printWithoutCrashing("The following subusers are registered.")
    try:
      user.operation.loadSubusersByName(subusersToList)
    except LookupError as ke:
      sys.exit(ke)
    for subuser in user.operation.subusers:
      if options.internal or not subuser.internal:
        if not options.long:
          subuserlib.print.printWithoutCrashing(subuser.name)
        else:
          subuser.describe()

  elif args[0] == 'installed-images':
    if options.json:
      subuserlib.print.printWithoutCrashing(json.dumps(user.installedImages.serializeToDict(),indent=1,separators=(",",": ")))
      sys.exit()
    if options.long:
      subuserlib.print.printWithoutCrashing("The following images are installed.")
    for id,installedImage in user.installedImages.items():
      if not options.long:
        try:
          identifier = installedImage.imageSource.getIdentifier()
          if not options.broken:
            subuserlib.print.printWithoutCrashing(identifier+" "+id)
        except KeyError:
          if options.broken:
            subuserlib.print.printWithoutCrashing(id)
      else:
        subuserlib.print.printWithoutCrashing("------------------")
        installedImage.describe()

  elif args[0] == 'image':
    if len(args) > 1:
      imagesToList = args[1:]
    for imageName in imagesToList:
      try:
        imageSource = subuserlib.resolve.resolveImageSource(user,imageName)
      except subuserlib.resolve.ResolutionError as e:
        sys.exit(str(e))
      if options.json:
        subuserlib.print.printWithoutCrashing(json.dumps(imageSource.serializeToDict(),indent=1,separators=(",",": ")))
      else:
        imageSource.describe()

  elif args[0] == 'repositories':
    if options.json:
      subuserlib.print.printWithoutCrashing(json.dumps(user.registry.repositories.serializeToDict(),indent=1,separators=(",",": ")))
      sys.exit()
    for name,repo in user.registry.repositories.items():
      if not options.long:
        subuserlib.print.printWithoutCrashing(repo.displayName)
      else:
        repo.describe()
        subuserlib.print.printWithoutCrashing("")

  else:
    sys.exit(args[0] + " cannot be listed. Option unrecognized. Use --help for help.")
