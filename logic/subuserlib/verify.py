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
# Python 2.x/Python 3 compatibility
try:
  input = raw_input
except NameError:
  raw_input = input

#internal imports
from subuserlib.classes.installationTask import InstallationTask
import subuserlib.classes.exceptions as exceptions
import subuserlib.classes.subuser

def verify(user,permissionsAccepter=None,checkForUpdatesExternally=False,subuserNames=[],prompt=False):
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
    (failedSubuserNames,permissionParsingExceptions) = approvePermissions(user,subuserNames,permissionsAccepter)
    subuserNames = [x for x in subuserNames if x not in failedSubuserNames]
    subuserNames += ensureServiceSubusersAreSetup(user,subuserNames)
    subusers = [user.getRegistry().getSubusers()[subuserName] for subuserName in subuserNames]
    installationTask = InstallationTask(user,subusersToBeUpdatedOrInstalled=subusers,checkForUpdatesExternally=checkForUpdatesExternally)
    outOfDateSubusers = installationTask.getOutOfDateSubusers()
    if outOfDateSubusers:
      user.getRegistry().log("New images for the following subusers need to be installed:")
      for subuser in outOfDateSubusers:
        user.getRegistry().log(subuser.getName())
      if (not prompt) or (prompt and (not raw_input("Would you like to install those images now? [Y/n]") == "n")):
        installationTask.updateOutOfDateSubusers()
    for exception in permissionParsingExceptions:
      user.getRegistry().log(str(exception))
    subusersWhosImagesFailedToBuild = installationTask.getSubusersWhosImagesFailedToBuild()
    if subusersWhosImagesFailedToBuild:
      user.getRegistry().log("Images for the following subusers failed to build:")
    for subuser in subusersWhosImagesFailedToBuild:
      user.getRegistry().log(subuser.getName())
    for subuser in subusers:
      try:
        subuser.getRunReadyImage().setup()
        subuser.setupHomeDir()
      except subuserlib.classes.subuserSubmodules.run.runtimeCache.NoRuntimeCacheForSubusersWhichDontHaveExistantImagesException:
        pass
  user.getInstalledImages().save()
  trimUnneededTempRepos(user)
  rebuildBinDir(user)
  cleanupRuntimeDirs(user)

def approvePermissions(user,subuserNames,permissionsAccepter):
  subusersWhosPermissionsFailedToParse = []
  exceptions = []
  for subuserName in subuserNames:
    subuser = user.getRegistry().getSubusers()[subuserName]
    try:
      userApproved = subuser.getPermissions()
    except subuserlib.classes.subuser.SubuserHasNoPermissionsException:
      userApproved = None
    try:
      oldDefaults = subuser.getPermissionsTemplate()
      newDefaults = subuser.getImageSource().getPermissions()
      permissionsAccepter.accept(subuser=subuser,oldDefaults=oldDefaults,newDefaults=newDefaults,userApproved=userApproved)
      subuser.getPermissionsTemplate().update(subuser.getImageSource().getPermissions())
      subuser.getPermissionsTemplate().save()
    except SyntaxError as e:
      subusersWhosPermissionsFailedToParse.append(subuserName)
      exceptions.append(e)
  return (subusersWhosPermissionsFailedToParse,exceptions)

def ensureServiceSubusersAreSetup(user,subuserNames):
  newServiceSubusers = []
  for subuserName in subuserNames:
    subuser = user.getRegistry().getSubusers()[subuserName]
    if not subuser.getPermissions()["gui"] is None:
      newServiceSubusers += subuser.getX11Bridge().setup()
  return newServiceSubusers

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

def cleanupRuntimeDirs(user):
  """
  Remove left overs that were not properly cleaned up after running subusers.
  """
  # Clean up ~/.subuser/volumes/execute
  executeDir = os.path.join(user.getConfig()["volumes-dir"],"execute")
  def is_process_running(process_id):
    """
    Taken from: http://stackoverflow.com/questions/7647167/check-if-a-process-is-running-in-python-in-linux-unix
    """
    try:
      os.kill(process_id, 0)
      return True
    except OSError:
      return False
  try:
    for pid in os.listdir(executeDir):
      try:
        numericPid = int(pid)
        if not is_process_running(numericPid):
          shutil.rmtree(os.path.join(executeDir,pid))
      except ValueError:
        pass
  except OSError:
    pass
