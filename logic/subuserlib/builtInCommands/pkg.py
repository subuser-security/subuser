#!/usr/bin/python3
# -*- coding: utf-8 -*-
#external imports
import sys
import optparse
import json
import os
import copy
#internal imports
from subuserlib.classes.user import User
import subuserlib.commandLineArguments
import subuserlib.permissions
from subuserlib.classes.permissionsAccepters.acceptPermissionsAtCLI import AcceptPermissionsAtCLI
from subuserlib.classes.permissions import Permissions
import subuserlib.profile
import subuserlib.test

def parseCliArgs(realArgs):
  usage = "usage: subuser pkg [init|add|test] IMAGE-SOURCE-NAMES <args>"
  description = """ Packaging subucommands. These commands are to be issued from the root of a subuser repository.

  init - Initialize a subuser repository.

  add - Add an image source to the repository.
  Usage: $ subuser pkg add image-source-name

  To test images use subuser dev --update <image-name>
  """
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--accept",dest="accept",action="store_true",default=False,help="When testing images, accept permissions without asking.")
  parser.add_option("--prompt",dest="prompt",action="store_true",default=False,help="Prompt before installing new images.")
  parser.add_option("--image-sources-dir", dest="imageSourcesDir",default=None,help="When initializing a new repository, set where the image source directories will be stored. This may be set when you are working with an existing git repository which you would like to unobtrusively add subuser image sources too.")
  parser.add_option("--permissions-file", dest="permissionsFile",default=None,help="When adding a new image source, the path to the new permissions.json file for the image source. Note: This flag should not be used to import permissions files from outside of the repository. Use the POSIX cp command for that.")
  parser.add_option("--image-file", dest="imageFile",default=None,help="When adding a new image source, the path to the new image file which will be used to build the image source. Note: This flag should not be used to import build files from outside of the repository. Use the POSIX cp command for that.")
  parser.add_option("--build-context", dest="buildContext",default=None,help="When adding a new image source, the path to the build context for building the image.")
  return parser.parse_args(args=realArgs)

defaultImageFileTemplate = """FROM-SUBUSER-IMAGE libx11@default
RUN apt-get update && apt-get upgrade -y && apt-get install -y PKG"""
defaultPermissions = copy.deepcopy(subuserlib.permissions.defaults)
if subuserlib.test.testing:
  defaultImageFileTemplate = """FROM-SUBUSER-IMAGE foo@default"""
  defaultPermissions["executable"] = "/usr/bin/nothing"

@subuserlib.profile.do_cprofile
def runCommand(realArgs):
  """
  Run packaging subcommands.
  """
  options,args = parseCliArgs(realArgs)
  try:
    subcommand = args[0]
    subcommands = ["init","add"]
    if not subcommand in subcommands:
      sys.exit(subcommand + " not a recognized subcommand of pkg. Use --help for help.")
  except IndexError:
    sys.exit("No command given, use -h for help.")
  user = User()
  if subcommand == "init":
    if not os.path.exists("./.subuser.json"):
      repoConfig = {}
      if options.imageSourcesDir:
        repoConfig["image-sources-dir"] = options.imageSourcesDir
      with user.getEndUser().get_file("./.subuser.json","w") as subuserDotJson:
        json.dump(repoConfig,subuserDotJson)
        if options.imageSourcesDir:
          user.getEndUser().makedirs(options.imageSourcesDir)
      subuserlib.print.printWithoutCrashing("Subuser repository initialized successfully!")
      subuserlib.print.printWithoutCrashing("You can add new image sources with:")
      subuserlib.print.printWithoutCrashing("$ subuser pkg add image-source-name")
    else:
      sys.exit("Subuser repository already initialized. Exiting.")
  if subcommand == "add":
    repo = subuserlib.resolve.getRepositoryFromPath(user,os.environ["PWD"])
    imageSourceToAdd = args[1]
    if imageSourceToAdd in repo:
      sys.exit("An image source named "+imageSourceToAdd+" is already present in the repository. Cannot add. Exiting.")
    subuserlib.print.printWithoutCrashing("Adding new image source "+imageSourceToAdd)
    useDefaultLocations = options.imageFile is None and options.permissionsFile is None and options.buildContext is None
    if useDefaultLocations:
      imageSourceDir = os.path.join(repo.getImageSourcesDir(),imageSourceToAdd)
      buildContext = os.path.join(imageSourceDir,"image")
      imageFile = os.path.join(buildContext,"SubuserImagefile")
      permissionsFile = os.path.join(imageSourceDir,"permissions.json")
      try:
        user.getEndUser().makedirs(buildContext)
      except OSError:
        pass
    else:
      if repo.getRepoConfig() is None:
        sys.exit("You must initialize your repository with 'pkg init' before adding image sources to it.")
      if options.buildContext is None or options.imageFile is None or options.permissionsFile is None:
        sys.exit("If you specify non-default paths you must specify all of them. That is --image-file, --build-context AND --permissions-file. Cannot add image. Exiting...")
      imageFile = options.imageFile
      try:
        user.getEndUser().makedirs(os.path.dirname(imageFile))
      except OSError:
        pass
      buildContext = options.buildContext
      try:
        user.getEndUser().makedirs(buildContext)
      except OSError:
        pass
      permissionsFile = options.permissionsFile
      try:
        user.getEndUser().makedirs(os.path.dirname(permissionsFile))
      except OSError:
        pass
      repoConfig = repo.getRepoConfig()
      if not "explicit-image-sources" in repoConfig:
        repoConfig["explicit-image-sources"] = {}
      repoConfig["explicit-image-sources"][imageSourceToAdd] = {"image-file":imageFile,"build-context":buildContext,"permissions-file":permissionsFile}
      with user.getEndUser().get_file("./.subuser.json","w") as subuserDotJson:
        json.dump(repoConfig,subuserDotJson,indent=1,separators=(",",": "))
    permissions = defaultPermissions
    (returncode,maintainerName,stderr) = user.getEndUser().callCollectOutput(["git","config","user.name"])
    subuserlib.print.printWithoutCrashing(stderr)
    (returncode,maintainerEmail,stderr) = user.getEndUser().callCollectOutput(["git","config","user.email"])
    subuserlib.print.printWithoutCrashing(stderr)
    permissions["maintainer"] = maintainerName.rstrip("\n")+" <"+maintainerEmail.rstrip("\n")+">"
    if not os.path.exists(permissionsFile):
      with user.getEndUser().get_file(permissionsFile,"w") as pf:
        json.dump(permissions,pf,indent=1,separators=(",",": "))
    while True:
      user.getEndUser().runEditor(permissionsFile)
      try:
        Permissions(user,initialPermissions=subuserlib.permissions.load(permissionsFilePath=permissionsFile),writePath=permissionsFile).save()
        break
      except SyntaxError as e:
        input(str(e)+"\nPress ENTER to edit the file again.")
    if not os.path.exists(imageFile):
      with user.getEndUser().get_file(imageFile,"w") as imgf:
        imgf.write(defaultImageFileTemplate)
    user.getEndUser().runEditor(imageFile)
    subuserlib.print.printWithoutCrashing("Your application has now been packaged. Run subuser dev %s to test your work. Use subuser dev --update %s to iterate."%(imageSourceToAdd,imageSourceToAdd))
