# -*- coding: utf-8 -*-

"""
High level operations on repostories.
"""

#external imports
import sys
#internal imports
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
    if repository.isPresent():
      user.getRegistry().getRepositories().addRepository(repository)
      user.getRegistry().commit()
    else:
      sys.exit("Cannot load repository, path or URL not found.")

def remove(user,name):
  user.getRegistry().getRepositories().removeRepository(name)
  user.getRegistry().commit()
