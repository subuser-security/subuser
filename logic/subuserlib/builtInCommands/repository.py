#!/usr/bin/python3
# -*- coding: utf-8 -*-
#external imports
import sys
import optparse
#internal imports
from subuserlib.classes.user import User
import subuserlib.resolve
import subuserlib.repository
import subuserlib.commandLineArguments
import subuserlib.profile

def parseCliArgs(sysargs):
  usage = "usage: subuser repository [options] [add|remove] NAME <URL>"
  description = """Add or remove a new named repository.

- EXAMPLE
    Add a new repository named foo with the URI http://www.example.com/repo.git.

    $ subuser repository add foo http://www.example.com/repo.git
    $ #You can also add a local repository:
    $ subuser repository add local-foo file:///home/timothy/my-local-repo/

- EXAMPLE
    Remove the repository named foo.

    $subuser repository remove foo

  """
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args(args=sysargs)

@subuserlib.profile.do_cprofile
def runCommand(sysargs):
  """
  Manage named subuser repositories.
  """
  options,args = parseCliArgs(sysargs)
  user = User()
  user.getRegistry().commit_message = " ".join(["subuser","repository"]+sysargs)
  try:
    action = args[0]
  except IndexError:
    sys.exit("Use subuser repository --help for help.")
  if action == "add":
    if not len(args) == 3:
      sys.exit("Use subuser repository --help for help.")
    name = args[1]
    url = args[2]
    with user.getRegistry().getLock():
      subuserlib.repository.add(user,name,url)
  elif action == "remove":
    if not len(args) == 2:
      sys.exit("Use subuser repository --help for help.")
    name = args[1]
    with user.getRegistry().getLock():
      subuserlib.repository.remove(user,name)
  else:
     sys.exit("Action "+args[0]+" not supported. Please see:\n subuser repository --help")
