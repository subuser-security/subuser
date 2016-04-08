#!/usr/bin/python3
# -*- coding: utf-8 -*-
#external imports
import sys
import optparse
#internal imports
from subuserlib.classes.user import User
import subuserlib.commandLineArguments
import subuserlib.removeOldImages
import subuserlib.profile

def parseCliArgs(realArgs):
  usage = "usage: subuser remove-old-images"
  description = """ Remove old, no longer used, installed images.  Note, once you do this, you will no longer be able to return to previous configuration states with subuser registry rollback or subuser update lock-subuser-to."""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--dry-run", dest="dryrun",action="store_true",default=False,help="Don't actually delete the images. Print which images would be deleted.")
  parser.add_option("--repo", dest="repoId",default=None,help="Only remove images from the given repository.")
  parser.add_option("--image-source", dest="imageSourceName",default=None,help="Remove old images from a specific image source. (Must be used in conjunction with --repo)")
  parser.add_option("-y", dest="yes",default=False,action="store_true",help="Don't ask, just delete unneeded images.")
  return parser.parse_args(args=realArgs)

@subuserlib.profile.do_cprofile
def runCommand(realArgs):
  """
  Remove images that are installed, but are not associated with any subusers.
  """
  options,args = parseCliArgs(realArgs)
  user = User()
  with user.getRegistry().getLock() as lockFileHandler:
    if not options.repoId is None:
      if not options.repoId in user.getRegistry().getRepositories():
        repo = subuserlib.resolve.lookupRepositoryByURI(user,options.repoId)
        if repo is None:
          sys.exit("The repository <"+options.repoId+"> does not exist.")
    else:
      repo = None
    subuserlib.removeOldImages.removeOldImages(user=user,dryrun=options.dryrun,yes=options.yes,sourceRepo=repo,imageSourceName=options.imageSourceName)
