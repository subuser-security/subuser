#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import sys
#internal imports
import subuserlib.classes.user,subuserlib.resolve,subuserlib.classes.repository

def add(user,name,url):
    repository = subuserlib.resolve.lookupRepositoryByURI(user,url)
    if repository:
      if repository.isTemporary():
        sys.exit("A temporary repository with this url already exists.  Cannot add.  The ability to uprade temporary repositories to named repositories is a wanted feature.  Feal free to send a quality, well thought out, pull request.")
      else:
        sys.exit("The repository named:" +repository.getName()+" already has this URL.  Cannot add.")
    else:
      repository = subuserlib.classes.repository.Repository(user,name=name,gitOriginURI=url,gitCommitHash="master")
      user.getRegistry().getRepositories().addRepository(repository)
      user.getRegistry().commit()

def remove(user,name):
      user.getRegistry().getRepositories().removeRepository(name)
