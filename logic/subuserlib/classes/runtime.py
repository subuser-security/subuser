#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
Runtime environements which are prepared for subusers to run in.
"""

#external imports
import sys,collections,os
#internal imports
import subuserlib.classes.userOwnedObject

def getRecursiveDirectoryContents(directory):
  files = []
  for (directory,_,fileList) in os.walk(directory):
    for fileName in fileList:
      files.append(os.path.join(directory,fileName))
  return files

class Runtime(subuserlib.classes.userOwnedObject.UserOwnedObject):
  __runReadyImageId = None
  __subuser = None
  __environment = None

  def __init__(self,user,subuser,runReadyImageId,environment):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self.__subuser = subuser
    self.__runReadyImageId = runReadyImageId

    self.__environment = environment

  def getSubuser(self):
    return self.__subuser

  def getRunreadyImageId(self):
    return self.__runReadyImageId

  def getEnvironment(self):
    return self.__environment

  def getSerialDevices(self):
    return [device for device in os.listdir("/dev/") if device.startswith("ttyS") or device.startswith("ttyUSB") or device.startswith("ttyACM")]
  
  def getBasicFlags(self):
    return [
      "-i",
      "-t",
      "--rm"]
  
  def passOnEnvVar(self,envVar):
    """
    Generate the arguments required to pass on a given ENV var to the container from the host.
    """
    try:
      return ["-e",envVar+"="+self.getEnvironment()[envVar]]
    except KeyError:
      return []

  def getSoundArgs(self):
    soundArgs = []
    if os.path.exists("/dev/snd"):
      soundArgs += ["--volume=/dev/snd:/dev/snd"]
      soundArgs += ["--device=/dev/snd/"+device for device in os.listdir("/dev/snd") if not device == "by-id" and not device == "by-path"]
    if os.path.exists("/dev/dsp"):
      soundArgs += ["--volume=/dev/dsp:/dev/dsp"]
      soundArgs += ["--device=/dev/dsp/"+device for device in os.listdir("/dev/dsp")]
    return soundArgs
  
  def getPermissionFlagDict(self):
    """
    This is a dictionary mapping permissions to functions which when given the permission's values return docker run flags.
    """
    return collections.OrderedDict([
     # Conservative permissions
     ("stateful-home", lambda p : ["-v="+self.getSubuser().getHomeDirOnHost()+":"+self.getSubuser().getDockersideHome()+":rw","-e","HOME="+self.getSubuser().getDockersideHome()] if p else ["-e","HOME="+self.getSubuser().getDockersideHome()]),
     ("inherit-locale", lambda p : self.passOnEnvVar("LANG")+self.passOnEnvVar("LANGUAGE") if p else []),
     ("inherit-timezone", lambda p : self.passOnEnvVar("TZ")+["-v=/etc/localtime:/etc/localtime:r"] if p else []),
     # Moderate permissions
     ("user-dirs", lambda userDirs : ["-v="+os.path.join(self.getSubuser().getUser().homeDir,userDir)+":"+os.path.join("/userdirs/",userDir)+":rw" for userDir in userDirs]),
     ("inherit-envvars", lambda envVars: [arg for var in envVars for arg in self.passOnEnvVar (var)]),
     ("sound-card", lambda p: self.getSoundArgs() if p else []),
     ("webcam", lambda p: ["--device=/dev/"+device for device in os.listdir("/dev/") if device.startswith("video")] if p else []),
     ("access-working-directory", lambda p: ["-v="+os.getcwd()+":/pwd:rw","--workdir=/pwd"] if p else ["--workdir="+self.getSubuser().getDockersideHome()]),
     ("allow-network-access", lambda p: ["--net=bridge","--dns=8.8.8.8"] if p else ["--net=none"]),
     # Liberal permissions
     ("x11", lambda p: ["-e","DISPLAY=unix"+os.environ['DISPLAY'],"-v=/tmp/.X11-unix:/tmp/.X11-unix:rw"] if p else []),
     ("graphics-card", lambda p: ["--device=/dev/dri/"+device for device in os.listdir("/dev/dri")] if p else []),
     ("serial-devices", lambda sd: ["--device=/dev/"+device for device in self.getSerialDevices()] if sd else []),
     ("system-dbus", lambda dbus: ["--volume=/var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket"] if dbus else []),
     ("as-root", lambda root: ["--user=0"] if root else ["--user="+str(os.getuid())]),
     # Anarchistic permissions
     ("privileged", lambda p: ["--privileged"] if p else [])])
  
  def getCommand(self,args):
    """
    Returns the command required to run the subuser as a list of string arguments.
    """
    flags = self.getBasicFlags()
    permissionFlagDict = self.getPermissionFlagDict()
    permissions = self.getSubuser().getPermissions()
    for permission, flagGenerator in permissionFlagDict.items():
      flags.extend(flagGenerator(permissions[permission]))
  
    return ["run"]+flags+[self.getRunreadyImageId()]+[self.getSubuser().getPermissions()["executable"]]+args
  
  def getPrettyCommand(self,args):
    """
    Get a command for pretty printing for use with dry-run.
    """
    command = self.getCommand(args)
    return "docker '"+"' '".join(command)+"'"
  
  def run(self,args):
    try:
      if not self.getSubuser().getPermissions()["executable"]:
        sys.exit("Cannot run subuser, no executable configured in permissions.json file.")
      def setupSymlinks():
        symlinkPath = os.path.join(self.getSubuser().getHomeDirOnHost(),"Userdirs")
        destinationPath = "/userdirs"
        if not os.path.exists(symlinkPath):
          try:
            os.makedirs(self.getSubuser().getHomeDirOnHost())
          except OSError:
            pass
          try:
            os.symlink(destinationPath,symlinkPath) #Arg, why are source and destination switched?
          #os.symlink(where does the symlink point to, where is the symlink)
          #I guess it's to be like cp...
          except OSError:
            pass
    
      if self.getSubuser().getPermissions()["stateful-home"]:
        setupSymlinks()
  
      self.getUser().getDockerDaemon().execute(self.getCommand(args))
    except KeyboardInterrupt:
      sys.exit(0)

