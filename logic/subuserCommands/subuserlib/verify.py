#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
This is one of the most important modules in subuser.  This module has one function `verify` which is used to apply the changes for most commands that change the user's configuration:

 - Adding a new subuser
 - Removing an old subuser
 - Updating repositories
 - Adding repositories
 - Repairing the instalation
"""

#external imports
#import ...
#internal imports
#import ...

def verify(user):
   """
   Ensure that:
      - Registry is consistent; warns the user about subusers that point to non-existant source programs.
     - For each subuser there is an up-to-date image installed.
     - No-longer-needed temporary repositories are removed. All temporary repositories have at least one subuser who's image is built from one of the repository's program sources.
      - No-longer-needed installed images are removed.
   """
  print("Verifying subuser configuration.")
  verifyRegistryConsistency(user)
  ensureUpToDateImagesAreInstalled(user)
  trimUnneededTempRepos(user)
  trimUnneededInstalledImages(user)

def verifyRegistryConsistency(user):
  print("Verifying registry consistency...")
  for _,subuser in user.getRegistry().getSubusers().iteritems():
    if not subuser.getProgramSource().getName() in subuser.getProgramSource().getRepository():
      print("WARNING: "+subuser.getName()+" is no longer present in it's source repository.") #TODO, find a way to recover the old permissions.

def ensureUpToDateImagesAreInstalled(user)
  print("Checking if images need to be updated or installed...")

def trimUnneededTempRepos(user)
  print("Running garbage collector on temporary repositories...")

def trimUnneededInstalledImages(user)
  print("Running garbage collector on installed images...")