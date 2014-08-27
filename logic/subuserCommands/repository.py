#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import optparse,sys
#internal imports
import subuserlib.classes.user,subuserlib.resolve,subuserlib.classes.repository

def parseCliArgs():
  usage = "usage: subuser %prog [options] [add|remove] NAME <URL>"
  description = """Add or remove a new named repository.

  Example:
  subuser repository add foo http://www.example.com/r.git

  Example:
  subuser repository remove foo

  """
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  advancedOptions = subuserlib.commandLineArguments.advancedInstallOptionsGroup(parser)
  parser.add_option_group(advancedOptions)
  return parser.parse_args()

#################################################################################################

options,args = parseCliArgs()

action = args[0]
user = subuserlib.classes.user.User()

if action == "add":
  if not len(args) == 3:
    sys.exit("Use subuser repository --help for help.")
  
  name = args[1]
  url = args[2]
  repository = getRepositoryFromURI(user,url)
  if repository:
    if type repository.getName() is int:
      sys.exit("A temporary repository with this url already exists.  Cannot add.  The ability to uprade temporary repositories to named repositories is a wanted feature.  Feal free to send a quality, well thought out, pull request.")
    else:
      sys.exit("The repository named:" +repository.getName()+" already has this URL.  Cannot add.")
  else:
    repository = subuserlib.classes.repository.Repository(user,name=name,gitOriginURI=url,gitCommitHash="master")
    user.getRegistry().getRepositories().addRepository(repository)
    user.getRegistry().commit()
elif action == "remove":
  if not len(args) == 2:
    sys.exit("Use subuser repository --help for help.")
  name = args[1]
  user.getRegistry().getRepositories().removeRepository(name)
