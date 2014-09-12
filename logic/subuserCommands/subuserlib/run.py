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
    "--rm"]

def getPermissionFlagDict(subuserToRun):
  """
  This is a dictionary mapping permissions to functions which when given the permission's values return docker run flags. 
  """
  return {
   "allow-network-access" : lambda p: ["--net=bridge"] if p else ["--net=none"],
   "system-dirs" : lambda systemDirs: ["-v="+systemDir+":"+systemDir+":ro" for systemDir in systemDirs],
   "user-dirs" : lambda userDirs : ["-v="+os.path.join(subuserToRun.getUser().homeDir,userDir)+":"+os.path.join("/userdirs/",userDir)+":rw" for userDir in userDirs],
   "access-working-directory" : lambda p: ["-v="+os.getcwd()+":/pwd:rw","--workdir=/pwd"] if p else ["--workdir="+subuserToRun.getDockersideHome()],
   "stateful-home" : lambda p : ["-v="+subuserToRun.getHomeDirOnHost()+":"+subuserToRun.getDockersideHome()+":rw","-e","HOME="+subuserToRun.getDockersideHome()] if p else [],
   "x11" : lambda p: ["-e","DISPLAY=unix"+os.environ['DISPLAY'],"-v=/tmp/.X11-unix:/tmp/.X11-unix:rw"] if p else [],
   "graphics-card" : lambda p:["-v=/dev/dri:/dev/dri:rw"] + ["--device=/dev/dri/"+device for device in os.listdir("/dev/dri")] if p else [],
   "sound-card" : lambda p: ["-v=/dev/snd:/dev/snd:rw"]+["--device=/dev/snd/"+device for device in os.listdir("/dev/snd") if not device == "by-id" and not device == "by-path"] if p else [], #Why the volume here?  To make it so that the device nodes are owned by the audio group ;).  Evil, I know...
   "webcam" : lambda p: ["--volume=/dev/"+device+":/dev/"+device for device in os.listdir("/dev/") if device.startswith("video")] + ["--device=/dev/"+device for device in os.listdir("/dev/") if device.startswith("video")] if p else [],
   "privileged" : lambda p: ["--privileged"] if p else [],
   "as-root" : lambda root: ["--user=0"] if root else ["--user="+str(os.getuid())]
   }

def getCommand(subuserToRun, imageArgs):
  """
  Returns the command requred to run the subuser as a list of string arguments.
  Exits, printing an error message, if the subuser cannot be run due to no proper image for it being installed.
  """
  if not(subuserToRun.getImageId() and subuserToRun.getImageId() in subuserToRun.getUser().getInstalledImages() and subuserToRun.getUser().getInstalledImages()[subuserToRun.getImageId()].isDockerImageThere()):
    sys.exit("Image for "+subuserToRun.getName()+" is not installed. Try running:\n $subuser repair")
  
  flags = getBasicFlags(subuserToRun)
  permissionFlagDict = getPermissionFlagDict(subuserToRun)
  permissions = subuserToRun.getPermissions()
  for permission, flagGenerator in permissionFlagDict.iteritems():
    flags.extend(flagGenerator(permissions[permission]))

  return ["run"]+flags+[subuserToRun.getImageId()]+[subuserToRun.getPermissions()["executable"]]+imageArgs

def getPrettyCommand(subuserToRun,imageArgs):
  """
  Get a command for pretty printing for use with dry-run.
  """
  command = getCommand(subuserToRun,imageArgs)
  return "docker '"+"' '".join(command)+"'"

def run(subuserToRun,imageArgs):
  def setupSymlinks():
    symlinkPath = os.path.join(subuserToRun.getHomeDirOnHost(),"Userdirs")
    destinationPath = "/userdirs"
    if not os.path.exists(symlinkPath):
      try:
        os.makedirs(subuserToRun.getHomeDirOnHost())
      except OSError:
        pass
      try:
        os.symlink(destinationPath,symlinkPath) #Arg, why are source and destination switched?
      #os.symlink(where does the symlink point to, where is the symlink)
      #I guess it's to be like cp...
      except OSError:
        pass

  if subuserToRun.getPermissions()["stateful-home"]:
    setupSymlinks()

  subuserToRun.getUser().getDockerDaemon().execute(getCommand(subuserToRun,imageArgs))
