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

    $ subuser repository add foo http://www.example.com/repo.git
    $ #You can also add a local repository:
    $ subuser repository add local-foo file:///home/timothy/my-local-repo/

- EXAMPLE
    Remove the repository named foo.

    $subuser repository remove foo

  """
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args(args=sysargs)

def repository(sysargs):
  """
  Manage named subuser repositories.

  Tests
  -----

  **Setup:**

  >>> import repository #import self

  Check our assumptions about the initial state of the test environment.

  >>> user = subuserlib.classes.user.User()
  >>> set(user.getRegistry().getRepositories().keys()) == set([u'default'])
  True

  Add a new repository named ``remote-repo``.

  >>> repository.repository(["add","remote-repo","file:///home/travis/remote-test-repo"])
  Adding new repository remote-repo

  See that it was actually successfully added.

  >>> user = subuserlib.classes.user.User()
  >>> set(user.getRegistry().getRepositories().keys()) == set([u'default', 'remote-repo'])
  True

  Remove the ``remote-repo`` repository.

  >>> repository.repository(["remove","remote-repo"])
  Removing repository remote-repo

  See that it was actually removed.

  >>> user = subuserlib.classes.user.User()
  >>> set(user.getRegistry().getRepositories().keys()) == set([u'default'])
  True


  Add a new repository named ``local-repo`` which is just a folder on the local system.

  >>> repository.repository(["add","local-repo","/home/travis/remote-test-repo"])
  Adding new repository local-repo

  See that it was actually successfully added.

  >>> user = subuserlib.classes.user.User()
  >>> set(user.getRegistry().getRepositories().keys()) == set([u'default', 'local-repo'])
  True

  Remove the ``local-repo`` repository.

  >>> repository.repository(["remove","local-repo"])
  Removing repository local-repo

  See that it was actually removed.

  >>> user = subuserlib.classes.user.User()
  >>> set(user.getRegistry().getRepositories().keys()) == set([u'default'])
  True

  """
  options,args = parseCliArgs(sysargs)
  user = subuserlib.classes.user.User()
  action = args[0]
  if action == "add":
    if not len(args) == 3:
      sys.exit("Use subuser repository --help for help.")
    name = args[1]
    url = args[2]
    try:
      with user.getRegistry().getLock():
        subuserlib.repository.add(user,name,url)
    except subuserlib.portalocker.portalocker.LockException:
      sys.exit("Another subuser process is currently running and has a lock on the registry. Please try again later.")
  elif action == "remove":
    if not len(args) == 2:
      sys.exit("Use subuser repository --help for help.")
    name = args[1]
    try:
      with user.getRegistry().getLock():
        subuserlib.repository.remove(user,name)
    except subuserlib.portalocker.portalocker.LockException:
      sys.exit("Another subuser process is currently running and has a lock on the registry. Please try again later.")

  else:
     sys.exit("Action "+args[0]+" not supported. Please see:\n subuser repository --help")

#################################################################################################

if __name__ == "__main__":
  repository(sys.argv[1:])

