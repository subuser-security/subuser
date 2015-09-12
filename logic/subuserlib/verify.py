#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
This is one of the most important modules in subuser.  This module has one function `verify` which is used to apply the changes for most commands that change the user's configuration:

 - Adding a new subuser
 - Removing an old subuser
 - Updating repositories
 - Adding repositories
 - Repairing the installation
"""

#external imports
import shutil
import os
#internal imports
import subuserlib.install
import subuserlib.classes.exceptions as exceptions

def verify(user,permissionsAccepter=None,checkForUpdatesExternally=False,subuserNames=[]):
  """
   Ensure that:
      - Registry is consistent; warns the user about subusers that point to non-existant source images.
     - For each subuser there is an up-to-date image installed.
     - No-longer-needed temporary repositories are removed. All temporary repositories have at least one subuser who's image is built from one of the repository's image sources.
     - No-longer-needed installed images are removed.
  """
  user.getRegistry().log("Verifying subuser configuration.")
  user.getRegistry().log("Verifying registry consistency...")
  for _,subuser in user.getRegistry().getSubusers().items():
    if not subuser.getImageSource().getName() in subuser.getImageSource().getRepository():
      user.getRegistry().log("WARNING: "+subuser.getName()+" is no longer present in it's source repository. Support for this progam may have been dropped.")
      try:
        subuserNames.remove(subuser.getName())
      except ValueError:
        pass
  user.getRegistry().log("Unregistering any non-existant installed images.")
  user.getInstalledImages().unregisterNonExistantImages()
  if subuserNames:
    user.getRegistry().setChanged(True)
    approvePermissions(user,subuserNames,permissionsAccepter)
    subuserNames += ensureServiceSubusersAreSetup(user,subuserNames)
    ensureImagesAreInstalledAndUpToDate(user,subuserNames=subuserNames,checkForUpdatesExternally=checkForUpdatesExternally)
  user.getInstalledImages().save()
  trimUnneededTempRepos(user)
  rebuildBinDir(user)

def approvePermissions(user,subuserNames,permissionsAccepter):
  for subuserName in subuserNames:
    subuser = user.getRegistry().getSubusers()[subuserName]
    try:
      userApproved = subuser.getPermissions()
    except subuserlib.classes.subuser.SubuserHasNoPermissionsException:
      userApproved = None
    permissionsAccepter.accept(subuser=subuser,oldDefaults=subuser.getPermissionsTemplate(),newDefaults=subuser.getImageSource().getPermissions(),userApproved=userApproved)
    subuser.getPermissionsTemplate().update(subuser.getImageSource().getPermissions())
    subuser.getPermissionsTemplate().save()

def ensureServiceSubusersAreSetup(user,subuserNames):
  newServiceSubusers = []
  for subuserName in subuserNames:
    subuser = user.getRegistry().getSubusers()[subuserName]
    if not subuser.getPermissions()["gui"] is None:
      if not subuser.getX11Bridge().isSetup():
        newServiceSubusers += subuser.getX11Bridge().setup(verify=False)
  return newServiceSubusers

def ensureImagesAreInstalledAndUpToDate(user,subuserNames,checkForUpdatesExternally=False):
  user.getRegistry().log("Checking if images need to be updated or installed...")
  subusersWhosImagesFailedToBuild = []
  for subuserName in subuserNames:
    subuser = user.getRegistry().getSubusers()[subuserName]
    if not subuser.locked(): # TODO: We should install images for locked subusers if their images have dissappered.
      try:
        subuserlib.install.ensureSubuserImageIsInstalledAndUpToDate(subuser,checkForUpdatesExternally=checkForUpdatesExternally)
        subuser.getRunReadyImage().setup()
      except exceptions.ImageBuildException as e:
        user.getRegistry().log(str(e))
        subusersWhosImagesFailedToBuild.append(subuser)
  if subusersWhosImagesFailedToBuild:
    user.getRegistry().log("Images for the following subusers failed to build:")
    for subuser in subusersWhosImagesFailedToBuild:
      user.getRegistry().log(subuser.getName())

def trimUnneededTempRepos(user):
  user.getRegistry().log("Running garbage collector on temporary repositories...")
  reposToRemove = []
  for repoId,repo in user.getRegistry().getRepositories().userRepositories.items():
    keep = False
    if repo.isTemporary():
      for _,installedImage in user.getInstalledImages().items():
        if repoId == installedImage.getSourceRepoId():
          keep = True
      for _,subuser in user.getRegistry().getSubusers().items():
        if repoId == subuser.getImageSource().getRepository().getName():
          keep = True
    else:
      keep = True
    if not keep:
      user.getRegistry().logChange("Removing uneeded temporary repository: "+repo.getDisplayName())
      repo.removeGitRepo()
      reposToRemove.append(repoId)
  for repoId in reposToRemove:
    del user.getRegistry().getRepositories().userRepositories[repoId]

def rebuildBinDir(user):
  if os.path.exists(user.getConfig()["bin-dir"]):
    shutil.rmtree(user.getConfig()["bin-dir"])
  os.mkdir(user.getConfig()["bin-dir"])
  for _,subuser in user.getRegistry().getSubusers().items():
    if subuser.isExecutableShortcutInstalled():
      subuser.installExecutableShortcut()
