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
def repository(sysargs):
  """
  Manage named subuser repositories.

  Tests
  -----

  **Setup:**

  >>> repository = __import__("subuser-repository") #import self

  Check our assumptions about the initial state of the test environment.

  >>> user = User()
  >>> set(user.getRegistry().getRepositories().keys()) == set([u'default'])
  True

  Add a new repository named ``remote-repo``.

  >>> repository.repository(["add","remote-repo","file:///home/travis/remote-test-repo"])
  Adding new repository remote-repo

  See that it was actually successfully added.

  >>> user = User()
  >>> set(user.getRegistry().getRepositories().keys()) == set([u'default', 'remote-repo'])
  True

  Remove the ``remote-repo`` repository.

  >>> repository.repository(["remove","remote-repo"])
  Removing repository remote-repo

  See that it was actually removed.

  >>> user = User()
  >>> set(user.getRegistry().getRepositories().keys()) == set([u'default'])
  True


  Add a new repository named ``local-repo`` which is just a folder on the local system.

  >>> repository.repository(["add","local-repo","/home/travis/remote-test-repo"])
  Adding new repository local-repo

  See that it was actually successfully added.

  >>> user = User()
  >>> set(user.getRegistry().getRepositories().keys()) == set([u'default', 'local-repo'])
  True

  Remove the ``local-repo`` repository.

  >>> repository.repository(["remove","local-repo"])
  Removing repository local-repo

  See that it was actually removed.

  >>> user = User()
  >>> set(user.getRegistry().getRepositories().keys()) == set([u'default'])
  True

  """
  options,args = parseCliArgs(sysargs)
  user = User()
  action = args[0]
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

#################################################################################################

if __name__ == "__main__":
  repository(sys.argv[1:])

