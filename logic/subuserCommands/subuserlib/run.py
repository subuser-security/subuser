#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import sys,os,getpass,subprocess,tempfile
#internal imports
import subuserlib.subprocessExtras

def getRecursiveDirectoryContents(directory):
  files = []
  for (directory,_,fileList) in os.walk(directory):
    for file in fileList:
      files.append(os.path.join(directory,file))
  return files

def getBasicFlags(subuserToRun):
  return [
    "-i",
    "-t",
    "--rm",
    "-v="+subuserToRun.getSetupSymlinksScriptPathOnHost()+":/launch/setup-symlinks",
    "-v="+subuserlib.paths.getDockersideScriptsPath()+":/launch/:ro"]

def getPermissionFlagDict(subuserToRun):
  """
  This is a dictionary mapping permissions to functions which when given the permission's values return docker run flags. 
  """
  return {
   "allow-network-access" : lambda p: ["--net=bridge"] if p else ["--net=none"],
   "system-dirs" : lambda systemDirs: ["-v="+systemDir+":"+systemDir+":ro" for systemDir in systemDirs],
   "user-dirs" : lambda userDirs : ["-v="+os.path.join(subuserToRun.getUser().homeDir,userDir)+":"+os.path.join("/userdirs/",userDir)+":rw" for userDir in userDirs],
   "inherit-working-directory" : lambda p: ["-v="+cwd+":/pwd:rw"] if p else [],
   "stateful-home" : lambda p : ["-v="+subuserToRun.getHomeDirOnHost()+":"+subuserToRun.getDockersideHome()+":rw"] if p else [],
   "x11" : lambda p: ["-e","DISPLAY=unix"+os.environ['DISPLAY'],"-v=/tmp/.X11-unix:/tmp/.X11-unix:rw"] if p else [],
   "graphics-card" : lambda p: ["--device=/dev/dri/"+device for device in os.listdir("/dev/dri")] if p else [],
   "sound-card" : lambda p: ["--device="+device for device in getRecursiveDirectoryContents("/dev/snd")] if p else [],
   "webcam" : lambda p: ["--device=/dev/"+device for device in os.listdir("/dev/") if device.startswith("video")] if p else [],
   "privileged" : lambda p: ["--privileged"] if p else []
   }

def getCommand(subuserToRun, programArgs):
  flags = getBasicFlags(subuserToRun)
  permissionFlagDict = getPermissionFlagDict(subuserToRun)
  permissions = subuserToRun.getPermissions()
  for permission, flagGenerator in permissionFlagDict.iteritems():
    flags.extend(flagGenerator(permissions[permission]))

  if not subuserToRun.getPermissions()["as-root"]:
    setupUserAndRunArgs = ["/launch/setupUserAndRun",subuserToRun.getUser().name]
  else:
    setupUserAndRunArgs ["/launch/runCommand","root"]

  return ["run"]+flags+[subuserToRun.getProgramSource().getImage().getImageID()]+setupUserAndRunArgs+[subuserToRun.getPermissions()["executable"]]+programArgs

def getPrettyCommand(subuserToRun,programArgs):
  """
  Get a command for pretty printing for use with dry-run.
  """
  command = getCommand(subuserToRun,programArgs)
  return "docker '"+"' '".join(command)+"'"

def run(subuserToRun,programArgs):
  def createSetupSymlinksScript():
    userDirs = subuserToRun.getPermissions()["user-dirs"]
    os.makedirs(dirname(subuserToRun.getSetupSymlinksScriptPathOnHost()))
    with open(subuserToRun.getSetupSymlinksScriptPathOnHost(),"w") as symlinkScrpt:
      symlinksScript.write("#!/bin/sh\n")
      symlinksScript.write("ln -s "+"/pwd/ "+self.getDockersideHome()+"/CurrentDirectoryOnHost")
      for userDir in userDirs:
        symlinksScript.write("ln -s /userdirs/"+userdir+" "+subuserToRun.getDockersideHomeDir()+"/"+userdir+"\n")

  createSetupSymlinksScript()
  subprocessExtras.subprocessCheckedCall(getCommand(subuserToRun,programArgs))
