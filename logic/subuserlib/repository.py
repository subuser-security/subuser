#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
High level operations on repostories.
"""

#external imports
import sys
#internal imports
from subuserlib.classes.user import User
import subuserlib.resolve
from subuserlib.classes.repository import Repository

def add(user,name,url):
  repository = subuserlib.resolve.lookupRepositoryByURIOrPath(user,url)
  if repository:
    if repository.isTemporary():
      sys.exit("A temporary repository with this url already exists.  Cannot add.  The ability to uprade temporary repositories to named repositories is a wanted feature.  Feal free to send a quality, well thought out, pull request.")
    else:
      sys.exit("The repository named:" +repository.getName()+" already has this URL.  Cannot add.")
  else:
    if url.startswith("/"):
      repository = Repository(user,name=name,sourceDir=url)
    else:
      repository = Repository(user,name=name,gitOriginURI=url,gitCommitHash="master")
    user.getRegistry().getRepositories().addRepository(repository)
    user.getRegistry().commit()

def remove(user,name):
  user.getRegistry().getRepositories().removeRepository(name)
  user.getRegistry().commit()

