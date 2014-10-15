#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import pathConfig
#external imports
import optparse,sys
#internal imports
import subuserlib.classes.user,subuserlib.resolve,subuserlib.repository,subuserlib.commandLineArguments

def parseCliArgs(sysargs):
  usage = "usage: subuser %prog [options] [add|remove] NAME <URL>"
  description = """Add or remove a new named repository.

- EXAMPLE
    Add a new repository named foo with the URI http://www.example.com/repo.git.

    $subuser repository add foo http://www.example.com/repo.git


- EXAMPLE
    Remove the repository named foo.

    $subuser repository remove foo

  """
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args(args=sysargs)

def repository(user,sysargs):
  """
  Manage named subuser repositories.

  Tests
  -----

  **Setup:**

  >>> import repository #import self
  >>> user = subuserlib.classes.user.User()

  Check our assumptions about the initial state of the test environment.

  >>> user.getRegistry().getRepositories().keys()
  [u'default']

  Add a new repository named ``remote-repo``.

  >>> repository.repository(user,["add","remote-repo","file:///home/travis/remote-test-repo"])
  Adding new repository remote-repo

  See that it was actually successfully added.

  >>> user.getRegistry().getRepositories().keys()
  [u'default', 'remote-repo']

  Remove the ``remote-repo`` repository.

  >>> repository.repository(user,["remove","remote-repo"])
  Removing repository remote-repo

  See that it was actually removed.

  >>> user.getRegistry().getRepositories().keys()
  [u'default']
  """
  options,args = parseCliArgs(sysargs)
  action = args[0]
  if action == "add":
    if not len(args) == 3:
      sys.exit("Use subuser repository --help for help.")
    name = args[1]
    url = args[2]
    subuserlib.repository.add(user,name,url)
  elif action == "remove":
    if not len(args) == 2:
      sys.exit("Use subuser repository --help for help.")
    name = args[1]
    subuserlib.repository.remove(user,name)
  else:
     sys.exit("Action "+args[0]+" not supported. Please see:\n subuser repository --help")

#################################################################################################

if __name__ == "__main__":
  user = subuserlib.classes.user.User()
  repository(user,sys.argv[1:])

