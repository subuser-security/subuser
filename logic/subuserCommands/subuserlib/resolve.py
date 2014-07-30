#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
This module is used to parse the program source identifiers used to identify program sources during instalation.  For more information see the program-source-identifiers section of the subuser standard.
"""

#external imports
#import ...
#internal imports
import subuserlib.classes.subuser, subuserlib.classes.repository, subuserlib.classes.programSource

def resolveProgramSource(user,programSourcePath,contextRepository="default"):
  """
  From a program source identifier path return a ProgamSource object. 

  >>> user = subuserlib.classes.user.User()
  >>> resolveProgramSource(user,"foo@default").getName()
  u'foo'

  If the repository identifier is a URI and a repository with the same URI already exists, then the URI is resolved to the name of the existing repository. Otherwise, a temporary repository is created.

  >>> resolveProgramSource(user,"bar@file:///root/subuser/test/remote-test-repo").getName()
  u'bar'

  Returns None if the path cannot be resolved due to the program source not existing.

  >>> resolveProgramSource(user,"non-existant-program-soruce@default")
  None

  Throws an error if the path is invalid or if the repository does not exist.
  """
