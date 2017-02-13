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
  user.registry.log("Verifying subuser configuration.")
  user.registry.log("Verifying registry consistency...",2)
  for subuser in subusers:
    try:
      subuser.imageSource
    except subuserlib.classes.subuser.NoImageSourceException:
      user.registry.log("WARNING: "+subuser.name+" is no longer present in it's source repository. Support for this progam may have been dropped.")
      try:
        subusers.remove(subuser)
      except ValueError:
        pass
  user.registry.log("Unregistering any non-existant installed images.",2)
  user.installedImages.unregisterNonExistantImages()
  user.registry.cleanOutOldPermissions()
  if subusers:
    user.registry.setChanged(True)
    user.registry.log("Approving permissions...",verbosityLevel=3)
    (failedSubusers,permissionParsingExceptions) = approvePermissions(user,subusers,permissionsAccepter)
    user.registry.log("Permissions approved...",verbosityLevel=3)
    subusers = [x for x in subusers if x not in failedSubusers]
    for failedSubuser in failedSubusers:
      try:
        failedSubuser.permissions
      except subuserlib.classes.subuser.SubuserHasNoPermissionsException:
        del user.registry.subusers[failedSubuser.name]
    subusers += ensureServiceSubusersAreSetup(user,subusers)
    installationTask = InstallationTask(user,subusersToBeUpdatedOrInstalled=subusers,checkForUpdatesExternally=checkForUpdatesExternally)
    outOfDateSubusers = installationTask.getOutOfDateSubusers()
    if outOfDateSubusers:
      user.registry.log("New images for the following subusers need to be installed:")
      for subuser in outOfDateSubusers:
        user.registry.log(subuser.name)
      if (not prompt) or (prompt and (not input("Would you like to install those images now? [Y/n]") == "n")):
        installationTask.updateOutOfDateSubusers(useCache=useCache)
    for exception in permissionParsingExceptions:
      user.registry.log(str(exception))
    subusersWhosImagesFailedToBuild = installationTask.getSubusersWhosImagesFailedToBuild()
    if subusersWhosImagesFailedToBuild:
      user.registry.log("Images for the following subusers failed to build:")
    for subuser in subusersWhosImagesFailedToBuild:
      user.registry.log(subuser.name)
    for subuser in subusers:
      try:
        subuser.getRunReadyImage().setup()
        subuser.setupHomeDir()
      except subuserlib.classes.subuserSubmodules.run.runtimeCache.NoRuntimeCacheForSubusersWhichDontHaveExistantImagesException:
        pass
  user.installedImages.save()
  trimUnneededTempRepos(user)
  rebuildBinDir(user)
  cleanupRuntimeDirs(user)
  cleanUpRuntimeCache(user)
  cleanUpAfterImproperlyTerminatedServices(user)
  user.registry.log("Verify complete.")

def approvePermissions(user,subusers,permissionsAccepter):
  subusersWhosPermissionsFailedToParse = []
  exceptions = []
  for subuser in subusers:
    if subuser.locked:
      continue
    try:
      userApproved = subuser.permissions
    except subuserlib.classes.subuser.SubuserHasNoPermissionsException:
      userApproved = None
    try:
      oldDefaults = subuser.getPermissionsTemplate()
      newDefaults = subuser.imageSource.permissions
      permissionsAccepter.accept(subuser=subuser,oldDefaults=oldDefaults,newDefaults=newDefaults,userApproved=userApproved)
      subuser.getPermissionsTemplate().update(subuser.imageSource.permissions)
      subuser.getPermissionsTemplate().save()
    except SyntaxError as e:
      subusersWhosPermissionsFailedToParse.append(subuser)
      exceptions.append(e)
    except subuserlib.classes.subuser.NoImageSourceException:
      subusersWhosPermissionsFailedToParse.append(subuser)
      user.registry.log("Warning: The image source for subuser %s is no longer available."%subuser.name)
  return (subusersWhosPermissionsFailedToParse,exceptions)

def ensureServiceSubusersAreSetup(user,subusers):
  newServiceSubusers = []
  for subuser in subusers:
    if subuser.permissions["gui"]:
      newServiceSubusers += subuser.x11Bridge.setup()
  return newServiceSubusers

def trimUnneededTempRepos(user):
  user.registry.log("Running garbage collector on temporary repositories...",2)
  reposToRemove = []
  for repoId,repo in user.registry.repositories.userRepositories.items():
    if repo.temporary and not repo.isInUse():
      user.registry.logChange("Removing uneeded temporary repository: "+repo.displayName)
      repo.removeGitRepo()
      reposToRemove.append(repoId)
  for repoId in reposToRemove:
    del user.registry.repositories.userRepositories[repoId]

def rebuildBinDir(user):
  if os.path.exists(user.config["bin-dir"]):
    shutil.rmtree(user.config["bin-dir"])
  user.endUser.mkdir(user.config["bin-dir"])
  for _,subuser in user.registry.subusers.items():
    if subuser.executableShortcutInstalled:
      subuser.installExecutableShortcut()
    if subuser.entryPointsExposed:
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
    user.registry.log("Clearing directory "+ pidDir,2)
    try:
      for pid in os.listdir(pidDir):
        try:
          numericPid = int(pid)
          if not is_process_running(numericPid):
            shutil.rmtree(os.path.join(pidDir,pid))
            user.registry.log("Removing "+ os.path.join(pidDir,pid)+" process is no longer running.",verbosityLevel=3)
          else:
            user.registry.log("Not removing "+ os.path.join(pidDir,pid)+" process is still running.",verbosityLevel=3)
        except ValueError:
          pass
    except OSError:
      pass
  # Clean up ~/.subuser/volumes/execute
  clearPIDSubdirs(os.path.join(user.config["volumes-dir"],"execute"))
  # Clean up ~/.subuser/volumes/x11
  clearPIDSubdirs(os.path.join(user.config["volumes-dir"],"x11"))

def cleanUpRuntimeCache(user):
  """
  Remove runtime cache directories for no longer existant images.
  """
  runtimeCacheDir = user.config["runtime-cache"]
  try:
    for imageId in os.listdir(runtimeCacheDir):
      if not imageId in user.installedImages:
        shutil.rmtree(os.path.join(runtimeCacheDir,imageId))
  except FileNotFoundError:
    pass

def cleanUpAfterImproperlyTerminatedServices(user):
  """
  Remove service lock files and service volumes in the case that a service has terminated improperly.
  """
  # Go through xpra volumes.
  try:
    xpraVolumeDir = os.path.join(user.config["volumes-dir"],"xpra")
    serviceVolumes = os.listdir(xpraVolumeDir)
    serviceLocksDir = os.path.join(user.config["lock-dir"],"services")
    serviceLockDirs = os.listdir(serviceLocksDir)
    subusersWithServiceDirs = set(serviceLockDirs) | set(serviceVolumes)
  except OSError:
    subusersWithServiceDirs = []
  for subuserWithServiceDirs in subusersWithServiceDirs:
    user.registry.log("Removing left over service files for subuser "+ subuserWithServiceDirs,2)
    if not subuserWithServiceDirs in user.registry.subusers:
      try:
        shutil.rmtree(os.path.join(xpraVolumeDir,subuserWithServiceDirs))
      except OSError as e:
        print(e)
      try:
        shutil.rmtree(os.path.join(serviceLocksDir,subuserWithServiceDirs))
      except OSError as e:
        print(e)
    else:
      user.registry.subusers[subuserWithServiceDirs].x11Bridge.cleanUpIfNotRunning()
