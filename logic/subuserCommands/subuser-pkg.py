#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

try:
  import pathConfig
except ImportError:
  pass
#external imports
import sys
import optparse
import json
import os
import copy

# Python 2.x/Python 3 compatibility
try:
    input = raw_input
except NameError:
    raw_input = input

#internal imports
from subuserlib.classes.user import User
import subuserlib.commandLineArguments
import subuserlib.packaging
import subuserlib.permissions
from subuserlib.classes.permissionsAccepters.acceptPermissionsAtCLI import AcceptPermissionsAtCLI
from subuserlib.classes.permissions import Permissions
import subuserlib.profile

def parseCliArgs(realArgs):
  usage = "usage: subuser pkg [init|add|test] IMAGE-SOURCE-NAMES <args>"
  description = """ Packaging subucommands. These commands are to be issued from the root of a subuser repository.

  init - Initialize a subuser repository.

  add - Add an image source to the repository.
  Usage: $ subuser pkg add image-source-name

  test - Test image sources by building and running them.
  Usage: $ subuser pkg test image-source-name
  Note: after running test, you may want to run ``$ subuser remove-old-images --repo=./``

  """
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--accept",dest="accept",action="store_true",default=False,help="When testing images, accept permissions without asking.")
  parser.add_option("--image-sources-dir", dest="imageSourcesDir",default=None,help="When initializing a new repository, set where the image source directories will be stored. This may be set when you are working with an existing git repository which you would like to unobtrusively add subuser image sources too.")
  parser.add_option("--permissions-file", dest="permissionsFile",default=None,help="When adding a new image source, the path to the new permissions.json file for the image source. Note: This flag should not be used to import permissions files from outside of the repository. Use the POSIX cp command for that.")
  parser.add_option("--image-file", dest="imageFile",default=None,help="When adding a new image source, the path to the new image file which will be used to build the image source. Note: This flag should not be used to import build files from outside of the repository. Use the POSIX cp command for that.")
  parser.add_option("--build-context", dest="buildContext",default=None,help="When adding a new image source, the path to the build context for building the image.")
  return parser.parse_args(args=realArgs)

@subuserlib.profile.do_cprofile
def pkg(realArgs):
  """
  Run packaging subcommands.
  """
  options,args = parseCliArgs(realArgs)
  user = User()
  subcommand = args[0]
  if subcommand == "init":
    if not os.path.exists("./.subuser.json"):
      repoConfig = {}
      if options.imageSourcesDir:
        repoConfig["image-sources-dir"] = options.imageSourcesDir
      with open("./.subuser.json","w") as subuserDotJson:
        json.dump(repoConfig,subuserDotJson)
        if options.imageSourcesDir:
          user.getEndUser().makedirs(options.imageSourcesDir)
      user.getEndUser().chown("./.subuser.json")
      print("Subuser repository initialized successfully!")
      print("You can add new image sources with:")
      print("$ subuser pkg add image-source-name")
    else:
      sys.exit("Subuser repository already initialized. Exiting.")
  if subcommand == "add":
    repo = subuserlib.resolve.getRepositoryFromPath(user,os.environ["PWD"])
    imageSourceToAdd = args[1]
    if imageSourceToAdd in repo:
      sys.exit("An image source named "+imageSourceToAdd+" is already present in the repository. Cannot add. Exiting.")
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
      if options.buildContext is None or options.imageFile is None or options.permissionsFile is None:
        sys.exit("If you specify non-default paths you must specify all of them. That is --image-file, --build-context AND --permissions-file. Cannot add image. Exiting...")
      imageFile = options.imageFile
      try:
        user.getEndUser().makedirs(os.path.dirname(imageFile))
      except OSError:
        pass
      buildContext = options.buildContext
      try:
        user.getEndUser().makedirs(os.path.dirname(buildContext))
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
      with open("./.subuser.json","w") as subuserDotJson:
        json.dump(repoConfig,subuserDotJson,indent=1,separators=(",",": "))
    permissions = copy.deepcopy(subuserlib.permissions.defaults)
    (returncode,maintainerName) = subuserlib.subprocessExtras.callCollectOutput(["git","config","user.name"])
    (returncode,maintainerEmail) = subuserlib.subprocessExtras.callCollectOutput(["git","config","user.email"])
    permissions["maintainer"] = maintainerName.rstrip("\n")+" <"+maintainerEmail.rstrip("\n")+">"
    if not os.path.exists(permissionsFile):
      with open(permissionsFile,"w") as pf:
        json.dump(permissions,pf,indent=1,separators=(",",": "))
    subuserlib.subprocessExtras.runEditor(permissionsFile)
    Permissions(user,initialPermissions=subuserlib.permissions.load(permissionsFilePath=permissionsFile),writePath=permissionsFile).save()
    user.getEndUser().chown(permissionsFile)
    if not os.path.exists(imageFile):
      with open(imageFile,"w") as imgf:
        imgf.write("""FROM-SUBUSER-IMAGE libx11@default
RUN apt-get update && apt-get upgrade -y && apt-get install -y PKG""")
      user.getEndUser().chown(imageFile)
    subuserlib.subprocessExtras.runEditor(imageFile)
    if raw_input("Would you like to test your new image? [Y/n]") == "n":
      sys.exit(0)
  if subcommand == "test" or subcommand == "add":
    user = User()
    repo = subuserlib.resolve.getRepositoryFromPath(user,os.environ["PWD"])
    permissionsAccepter = AcceptPermissionsAtCLI(user,alwaysAccept = options.accept)
    imageSourceNames=args[1:]
    with user.getRegistry().getLock() as lockFileHandler:
      subuserNames = []
      subuserNamePrefix = "!test-image-subuser-"
      # Build the images
      for imageSourceName in imageSourceNames:
        subuserName = subuserNamePrefix+imageSourceName
        subuserNames.append(subuserName)
        subuserlib.subuser.addFromImageSourceNoVerify(user,subuserName,repo[imageSourceName])
      subuserlib.verify.verify(user,subuserNames=subuserNames,permissionsAccepter=permissionsAccepter)
      for subuserName in subuserNames:
        if user.getRegistry().getSubusers()[subuserName].getImageId() is None and not raw_input(subuserName+" failed to build. Edit its image file and try again? [Y/n]") == "n":
          subuserlib.subprocessExtras.runEditor(user.getRegistry().getSubusers()[subuserName].getImageSource().getImageFile())
          subuserlib.verify.verify(user,subuserNames=[subuserName],permissionsAccepter=permissionsAccepter)
      user.getRegistry().commit()
      # Create a list of the names of the new subusers
      subuserNames = []
      for imageSourceName in imageSourceNames:
        subuserNames.append(subuserNamePrefix+imageSourceName)
      # Run the images
      for subuserName in subuserNames:
        arguments = raw_input("Running "+subuserName+" enter arguments and press enter to continue:")
        arguments = arguments.split(" ")
        if arguments == [""]:
          arguments = []
        subuser = user.getRegistry().getSubusers()[subuserName]
        if subuser.getPermissions()["executable"]:
          runtime = subuser.getRuntime(os.environ)
          if runtime:
            runtime.run(arguments)
      # Remove the subusers
      subuserlib.subuser.remove(user,subuserNames)

#################################################################################################

if __name__ == "__main__":
  pkg(sys.argv[1:])
