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
import shutil,os
#internal imports
import subuserlib.install

def verify(user):
  """
   Ensure that:
      - Registry is consistent; warns the user about subusers that point to non-existant source images.
     - For each subuser there is an up-to-date image installed.
     - No-longer-needed temporary repositories are removed. All temporary repositories have at least one subuser who's image is built from one of the repository's image sources.
      - No-longer-needed installed images are removed.
  """
  user.getRegistry().log("Verifying subuser configuration.")
  verifyRegistryConsistency(user)
  user.getRegistry().log("Unregistering any non-existant installed images.")
  user.getInstalledImages().unregisterNonExistantImages()
  ensureImagesAreInstalledAndUpToDate(user)
  user.getInstalledImages().save()
  trimUnneededTempRepos(user)
  rebuildBinDir(user)

def verifyRegistryConsistency(user):
  user.getRegistry().log("Verifying registry consistency...")
  for _,subuser in user.getRegistry().getSubusers().iteritems():
    if not subuser.getImageSource().getName() in subuser.getImageSource().getRepository():
      user.getRegistry().log("WARNING: "+subuser.getName()+" is no longer present in it's source repository. Support for this progam may have been dropped.")

def ensureImagesAreInstalledAndUpToDate(user):
  user.getRegistry().log("Checking if images need to be updated or installed...")
  for _,subuser in user.getRegistry().getSubusers().iteritems():
    subuserlib.install.ensureSubuserImageIsInstalledAndUpToDate(subuser)    

def trimUnneededTempRepos(user):
  user.getRegistry().log("Running garbage collector on temporary repositories...")
  reposToRemove = []
  for repoId,repo in user.getRegistry().getRepositories().userRepositories.iteritems():
    keep = False
    if repo.isTemporary():
      for _,installedImage in user.getInstalledImages().iteritems():
        if repoId == installedImage.getSourceRepoId():
          keep = True
    else:
      keep = True
    if not keep:
      user.getRegistry().logChange("Removing uneeded temporary repository: "+repo.getGitOriginURI())
      repo.removeGitRepo()
      reposToRemove.append(repoId)
  for repoId in reposToRemove:
    del user.getRegistry().getRepositories().userRepositories[repoId]

def rebuildBinDir(user):
  if os.path.exists(user.getConfig().getBinDir()):
    shutil.rmtree(user.getConfig().getBinDir())
  os.mkdir(user.getConfig().getBinDir())
  for _,subuser in user.getRegistry().getSubusers().iteritems():
    if subuser.isExecutableShortcutInstalled():
      subuser.installExecutableShortcut()
