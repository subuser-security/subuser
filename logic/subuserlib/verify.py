# -*- coding: utf-8 -*-

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
from subuserlib.classes.installationTask import InstallationTask
import subuserlib.classes.exceptions as exceptions
import subuserlib.classes.subuser

def verify(user,permissionsAccepter=None,checkForUpdatesExternally=False,subusers=[],prompt=False,useCache=False):
  """
   Ensure that:
     - Registry is consistent; warns the user about subusers that point to non-existant source images.
     - For each subuser there is an up-to-date image installed.
     - No-longer-needed temporary repositories are removed. All temporary repositories have at least one subuser who's image is built from one of the repository's image sources.
     - No-longer-needed installed images are removed.
  """
  user.getRegistry().log("Verifying subuser configuration.")
  user.getRegistry().log("Verifying registry consistency...")
  for subuser in subusers:
    try:
      subuser.getImageSource()
    except subuserlib.classes.subuser.NoImageSourceException:
      user.getRegistry().log("WARNING: "+subuser.getName()+" is no longer present in it's source repository. Support for this progam may have been dropped.")
      try:
        subusers.remove(subuser)
      except ValueError:
        pass
  user.getRegistry().log("Unregistering any non-existant installed images.")
  user.getInstalledImages().unregisterNonExistantImages()
  user.getRegistry().cleanOutOldPermissions()
  if subusers:
    user.getRegistry().setChanged(True)
    user.getRegistry().log("Approving permissions...",verbosityLevel=3)
    (failedSubusers,permissionParsingExceptions) = approvePermissions(user,subusers,permissionsAccepter)
    user.getRegistry().log("Permissions approved...",verbosityLevel=3)
    subusers = [x for x in subusers if x not in failedSubusers]
    for failedSubuser in failedSubusers:
      try:
        failedSubuser.getPermissions()
      except subuserlib.classes.subuser.SubuserHasNoPermissionsException:
        del user.getRegistry().getSubusers()[failedSubuser.getName()]
    subusers += ensureServiceSubusersAreSetup(user,subusers)
    installationTask = InstallationTask(user,subusersToBeUpdatedOrInstalled=subusers,checkForUpdatesExternally=checkForUpdatesExternally)
    outOfDateSubusers = installationTask.getOutOfDateSubusers()
    if outOfDateSubusers:
      user.getRegistry().log("New images for the following subusers need to be installed:")
      for subuser in outOfDateSubusers:
        user.getRegistry().log(subuser.getName())
      if (not prompt) or (prompt and (not input("Would you like to install those images now? [Y/n]") == "n")):
        installationTask.updateOutOfDateSubusers(useCache=useCache)
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
  cleanUpRuntimeCache(user)
  cleanUpAfterImproperlyTerminatedServices(user)

def approvePermissions(user,subusers,permissionsAccepter):
  subusersWhosPermissionsFailedToParse = []
  exceptions = []
  for subuser in subusers:
    if subuser.locked():
      continue
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
      subusersWhosPermissionsFailedToParse.append(subuser)
      exceptions.append(e)
    except subuserlib.classes.subuser.NoImageSourceException:
      subusersWhosPermissionsFailedToParse.append(subuser)
      user.getRegistry().log("Warning: The image source for subuser %s is no longer available."%subuser.getName())
  return (subusersWhosPermissionsFailedToParse,exceptions)

def ensureServiceSubusersAreSetup(user,subusers):
  newServiceSubusers = []
  for subuser in subusers:
    if not subuser.getPermissions()["gui"] is None:
      newServiceSubusers += subuser.getX11Bridge().setup()
  return newServiceSubusers

def trimUnneededTempRepos(user):
  user.getRegistry().log("Running garbage collector on temporary repositories...")
  reposToRemove = []
  for repoId,repo in user.getRegistry().getRepositories().userRepositories.items():
    if repo.isTemporary() and not repo.isInUse():
      user.getRegistry().logChange("Removing uneeded temporary repository: "+repo.getDisplayName())
      repo.removeGitRepo()
      reposToRemove.append(repoId)
  for repoId in reposToRemove:
    del user.getRegistry().getRepositories().userRepositories[repoId]

def rebuildBinDir(user):
  if os.path.exists(user.getConfig()["bin-dir"]):
    shutil.rmtree(user.getConfig()["bin-dir"])
  user.getEndUser().mkdir(user.getConfig()["bin-dir"])
  for _,subuser in user.getRegistry().getSubusers().items():
    if subuser.isExecutableShortcutInstalled():
      subuser.installExecutableShortcut()
    if subuser.areEntryPointsExposed():
      subuser.exposeEntrypoints()

def cleanupRuntimeDirs(user):
  """
  Remove left overs that were not properly cleaned up after running subusers.
  """
  def is_process_running(process_id):
    """
    Taken from: http://stackoverflow.com/questions/7647167/check-if-a-process-is-running-in-python-in-linux-unix
    """
    try:
      os.kill(process_id, 0)
      return True
    except OSError:
      return False
  def clearPIDSubdirs(pidDir):
    """
    Clear out a directory containing subdirectories named with the PIDs of processes by removing any directories corresponding to non-running processes.
    """
    user.getRegistry().log("Clearing directory "+ pidDir)
    try:
      for pid in os.listdir(pidDir):
        try:
          numericPid = int(pid)
          if not is_process_running(numericPid):
            shutil.rmtree(os.path.join(pidDir,pid))
            user.getRegistry().log("Removing "+ os.path.join(pidDir,pid)+" process is no longer running.",verbosityLevel=3)
          else:
            user.getRegistry().log("Not removing "+ os.path.join(pidDir,pid)+" process is still running.",verbosityLevel=3)
        except ValueError:
          pass
    except OSError:
      pass
  # Clean up ~/.subuser/volumes/execute
  clearPIDSubdirs(os.path.join(user.getConfig()["volumes-dir"],"execute"))
  # Clean up ~/.subuser/volumes/x11
  clearPIDSubdirs(os.path.join(user.getConfig()["volumes-dir"],"x11"))

def cleanUpRuntimeCache(user):
  """
  Remove runtime cache directories for no longer existant images.
  """
  runtimeCacheDir = user.getConfig()["runtime-cache"]
  try:
    for imageId in os.listdir(runtimeCacheDir):
      if not imageId in user.getInstalledImages():
        shutil.rmtree(os.path.join(runtimeCacheDir,imageId))
  except FileNotFoundError:
    pass

def cleanUpAfterImproperlyTerminatedServices(user):
  """
  Remove service lock files and service volumes in the case that a service has terminated improperly.
  """
  # Go through xpra volumes.
  try:
    xpraVolumeDir = os.path.join(user.getConfig()["volumes-dir"],"xpra")
    serviceVolumes = os.listdir(xpraVolumeDir)
    serviceLocksDir = os.path.join(user.getConfig()["lock-dir"],"services")
    serviceLockDirs = os.listdir(serviceLocksDir)
    subusersWithServiceDirs = set(serviceLockDirs) | set(serviceVolumes)
  except OSError:
    subusersWithServiceDirs = []
  for subuserWithServiceDirs in subusersWithServiceDirs:
    user.getRegistry().log("Removing left over service files for subuser "+ subuserWithServiceDirs)
    if not subuserWithServiceDirs in user.getRegistry().getSubusers():
      try:
        shutil.rmtree(os.path.join(xpraVolumeDir,subuserWithServiceDirs))
      except OSError as e:
        print(e)
      try:
        shutil.rmtree(os.path.join(serviceLocksDir,subuserWithServiceDirs))
      except OSError as e:
        print(e)
    else:
      user.getRegistry().getSubusers()[subuserWithServiceDirs].getX11Bridge().cleanUpIfNotRunning()
