#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import sys
import os
import getpass
import subprocess
import tempfile

import subuserlib.permissions
import subuserlib.dockerImages
import subuserlib.docker
import subuserlib.update
###############################################################
username = getpass.getuser()
cwd = os.getcwd()
home = os.path.expanduser("~")
###############################################################

def getAllowNetworkAccessArg(permissions):
  if subuserlib.permissions.getAllowNetworkAccess(permissions):
    return "--networking=true"
  else:
    return "--networking=false"

def setupHostSubuserHome(home):
  if not os.path.exists(home):
    os.makedirs(home)

def getAndSetupHostSubuserHome(programName,permissions):
  if subuserlib.permissions.getStatefulHome(permissions):
    hostSubuserHome = subuserlib.paths.getProgramHomeDirOnHost(programName)
  else:
    hostSubuserHome = tempfile.mkdtemp(prefix="subuser-"+programName)

  setupHostSubuserHome(hostSubuserHome)
  return hostSubuserHome
 
def makeSystemDirVolumeArgs(systemDirs):
  return ["-v="+systemDir+":"+systemDir+":ro" for systemDir in systemDirs]

def getAndSetupUserDirVolumes(permissions,hostSubuserHome,dry):
  """ Sets up the user directories to be shared between the host user and the subuser-program.
Returns volume arguments to be passed to docker run"""
  def setupUserDirSymlinks(userDirs):
    """ Create symlinks to userdirs in program's home dir. """
    for userDir in userDirs:
      source = os.path.join("/userdirs/",userDir)
      destination = os.path.join(hostSubuserHome,userDir)
      if not os.path.islink(destination):
        os.symlink(source,destination)

  userDirs = subuserlib.permissions.getUserDirs(permissions)
  if not dry:
    setupUserDirSymlinks(userDirs)
  userDirVolumeArgs = makeUserDirVolumeArgs(userDirs)
  return userDirVolumeArgs

def makeUserDirVolumeArgs(userDirs):
  return ["-v="+os.path.join(home,userDir)+":"+os.path.join("/userdirs/",userDir)+":rw" for userDir in userDirs]

def getSetupUserAndRunArgs(permissions):
  if not subuserlib.permissions.getAsRoot(permissions):
    setupUserAndRunPath = "/launch/setupUserAndRun"
    return [setupUserAndRunPath,username]
  else:
    return ["/launch/runCommand","root"]

def getWorkingDirectoryVolumeArg(permissions):
  if subuserlib.permissions.getInheritWorkingDirectory(permissions):
    return ["-v="+cwd+":/home/pwd:rw"]
  else:
    return []

def getDockersideHome(permissions):
  if subuserlib.permissions.getAsRoot(permissions):
    return "/root/"
  else:
    return home

def getAndSetupVolumes(programName,permissions,dry):
  """ 
Sets up the volumes which will be shared between the host and the subuser program.

Returns a list of volume mounting arguments to be passed to docker run.
"""

  hostSubuserHome = getAndSetupHostSubuserHome(programName,permissions) 

  dockersideScriptsPath = subuserlib.paths.getDockersideScriptsPath()
  dockersideBinPath = "/launch"
  dockersidePWDPath = os.path.join("/home","pwd")

  systemDirVolumeArgs = makeSystemDirVolumeArgs(subuserlib.permissions.getSystemDirs(permissions))

  userDirVolumeArgs = getAndSetupUserDirVolumes(permissions,hostSubuserHome,dry)

  workingDirectoryVolumeArg = getWorkingDirectoryVolumeArg(permissions)

  dockersideHome = getDockersideHome(permissions)

  volumeArgs = ["-v="+hostSubuserHome+":"+dockersideHome+":rw"
    ,"-v="+dockersideScriptsPath+":"+dockersideBinPath+":ro"] + workingDirectoryVolumeArg + systemDirVolumeArgs + userDirVolumeArgs

  def cleanUpVolumes():
    if not subuserlib.permissions.getStatefulHome(permissions):
      subprocess.call(["rm","-rf",hostSubuserHome])

  return (volumeArgs,cleanUpVolumes)

def getX11Args(permissions):
  if subuserlib.permissions.getX11(permissions):
    return ["-e","DISPLAY=unix"+os.environ['DISPLAY'],"-v=/tmp/.X11-unix:/tmp/.X11-unix:rw"]
  else:
    return []

def getGraphicsCardArgs(permissions):
  if subuserlib.permissions.getGraphicsCard(permissions):
    return  ["-v=/dev/dri:/dev/dri:rw","-lxc-conf=lxc.cgroup.devices.allow = c 226:* rwm"]
  else:
    return []

def getSoundCardArgs(permissions):
  if subuserlib.permissions.getSoundCard(permissions):
    return  ["-v=/dev/snd:/dev/snd:rw","-lxc-conf=lxc.cgroup.devices.allow = c 116:* rwm"]
  else:
    return []

def getWebcamArgs(permissions):
  if subuserlib.permissions.getWebcam(permissions):
    cameraVolumes = []
    for device in os.listdir("/dev/"):
      if device.startswith("video"):
        cameraVolumes.append("-v=/dev/"+device+":/dev/"+device+":rw")
    return  cameraVolumes+["-lxc-conf=lxc.cgroup.devices.allow = c 81:* rwm"]
  else:
    return []

def getPrivilegedArg(permissions):
  if subuserlib.permissions.getPrivileged(permissions):
    return ["-privileged"]
  else:
    return []

def getDockerArguments(programName,programArgs,dry):
  dockerImageName = subuserlib.dockerImages.getImageTagOfInstalledProgram(programName)
  permissions = subuserlib.permissions.getPermissions(programName)
  allowNetworkAccessArg = getAllowNetworkAccessArg(permissions)
  executable = subuserlib.permissions.getExecutable(permissions)
  setupUserAndRunArgs = getSetupUserAndRunArgs(permissions)
  x11Args = getX11Args(permissions)
  graphicsCardArgs = getGraphicsCardArgs(permissions)
  soundCardArgs = getSoundCardArgs(permissions)
  webcamArgs = getWebcamArgs(permissions)
  privilegedArg = getPrivilegedArg(permissions)
  (volumeArgs,cleanUpVolumes) = getAndSetupVolumes(programName,permissions,dry)
  dockerArgs = ["run","-i","-t","-rm",allowNetworkAccessArg]+privilegedArg+volumeArgs+x11Args+graphicsCardArgs+soundCardArgs+webcamArgs+[dockerImageName]+setupUserAndRunArgs+[executable]+programArgs
  return (dockerArgs,cleanUpVolumes)

def showDockerCommand(dockerArgs):
  print("""If this wasn't a dry run, the following command would be executed.

Please note: This is for testing purposes only, and this command is not guaranteed to work.""")
  print("docker '"+"' '".join(dockerArgs)+"'")

def runProgram(programName,programArgs,dry=False):
  if subuserlib.update.needsUpdate(programName):
   print("""This program needs to be updated.  You can do so with:

$ subuser update

Trying to run anyways:
""")
  (dockerArgs,cleanUpVolumes) = getDockerArguments(programName,programArgs,dry)
  if not dry:
   subuserlib.docker.runDocker(dockerArgs)
  else:
   showDockerCommand(dockerArgs)
  cleanUpVolumes()
