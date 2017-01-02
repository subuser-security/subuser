# -*- coding: utf-8 -*-

"""
Runtime environments which are prepared for subusers to run in.
"""

#external imports
import sys
import collections
import os
import time
import binascii
import struct
import shutil
#internal imports
import subuserlib.test
from subuserlib.classes.userOwnedObject import UserOwnedObject

def getRecursiveDirectoryContents(directory):
  files = []
  for (directory,_,fileList) in os.walk(directory):
    for fileName in fileList:
      files.append(os.path.join(directory,fileName))
  return files

class Runtime(UserOwnedObject):
  def __init__(self,user,subuser,environment,extraDockerFlags=None,entrypoint = None):
    self.__subuser = subuser
    self.__environment = environment
    self.__backgroundSuppressOutput = True
    self.__backgroundCollectStdout = False
    self.__backgroundCollectStderr = False
    self.__executionSpoolReader = None
    if extraDockerFlags is None:
      self.__extraFlags = []
    else:
      self.__extraFlags = extraDockerFlags
    if not entrypoint:
      self.entrypoint = self.getSubuser().getPermissions()["executable"]
    else:
      self.entrypoint = entrypoint
    self.__background = False
    if not subuserlib.test.testing:
      self.__hostname = binascii.b2a_hex(os.urandom(10)).decode()
    else:
      self.__hostname = "<random-hostname>"
    UserOwnedObject.__init__(self,user)

  def getSubuser(self):
    return self.__subuser

  def getRunReadyImageId(self):
    try:
      return self.getSubuser().getRunReadyImage().getId()
    except KeyError:
      sys.exit("""No run ready image is prepaired for this subuser. Please run:

$ subuser repair
""")

  def getEnvironment(self):
    return self.__environment

  def getEnvvar(self,var):
    try:
      return self.getEnvironment()[var]
    except KeyError:
      sys.exit("The env var %s is not set. Are you sure you are running as a normal user?" % var)

  def getSerialDevices(self):
    return [device for device in os.listdir("/dev/") if device.startswith("ttyS") or device.startswith("ttyUSB") or device.startswith("ttyACM")]

  def getCidFile(self):
    return "/tmp/subuser-"+self.getSubuser().getName()

  def getBasicFlags(self):
    common = ["--rm"]
    if self.getBackground():
      return common + ["--cidfile",self.getCidFile()]
    else:
      if sys.stdout.isatty() and sys.stdin.isatty():
        return common + ["-i","-t"]
      else:
        return common + ["-i"]

  def logIfInteractive(self,message):
    if sys.stdout.isatty():
      print(message)

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
      soundArgs += ["--volume=/dev/snd:/dev/snd:ro"]
      soundArgs += ["--device=/dev/snd/"+device for device in os.listdir("/dev/snd") if not device == "by-id" and not device == "by-path"]
    if os.path.exists("/dev/dsp"):
      soundArgs += ["--volume=/dev/dsp:/dev/dsp:ro"]
      if os.path.isdir('/dev/dsp'):
        soundArgs += ["--device=/dev/dsp/"+device for device in os.listdir("/dev/dsp")]
      else:
        soundArgs += ["--device=/dev/dsp"]
    return soundArgs

  def getPermissionFlagDict(self):
    """
    This is a dictionary mapping permissions to functions which when given the permission's values return docker run flags.
    """
    return collections.OrderedDict([
     # Conservative permissions
     ("stateful-home", lambda p : ["--volume="+self.getSubuser().getHomeDirOnHost()+":"+self.getSubuser().getDockersideHome()+":rw","-e","HOME="+self.getSubuser().getDockersideHome()] if p else ["-e","HOME="+self.getSubuser().getDockersideHome()]),
     ("inherit-locale", lambda p : self.passOnEnvVar("LANG")+self.passOnEnvVar("LANGUAGE") if p else []),
     ("inherit-timezone", lambda p : self.passOnEnvVar("TZ")+["--volume=/etc/localtime:/etc/localtime:ro"] if p else []),
     # Moderate permissions
     ("gui", lambda p : ["-e","DISPLAY=unix:100","--volume",self.getSubuser().getX11Bridge().getServerSideX11Path()+":/tmp/.X11-unix:rw"] if p else []),
     ("user-dirs", lambda userDirs : ["--volume="+os.path.join(self.getSubuser().getUser().getEndUser().homeDir,userDir)+":"+os.path.join("/subuser/userdirs/",userDir)+":rw" for userDir in userDirs]),
     ("inherit-envvars", lambda envVars: [arg for var in envVars for arg in self.passOnEnvVar (var)]),
     ("sound-card", lambda p: self.getSoundArgs() if p else []),
     ("webcam", lambda p: ["--device=/dev/"+device for device in os.listdir("/dev/") if device.startswith("video")] if p else []),
     ("access-working-directory", lambda p: ["--volume="+os.getcwd()+":/pwd:rw","--workdir=/pwd"] if p else ["--workdir="+self.getSubuser().getDockersideHome()]),
     ("allow-network-access", lambda p: ["--net=bridge"] if p else ["--net=none"]),
     # Liberal permissions
     ("x11", lambda p: ["-e","DISPLAY=unix"+self.getEnvvar('DISPLAY'),"--volume=/tmp/.X11-unix:/tmp/.X11-unix:rw","--volume="+self.getXautorityFilePath()+":/subuser/.Xauthority:ro","-e","XAUTHORITY=/subuser/.Xauthority"] if p else []),
     ("system-dirs", lambda systemDirs : ["--volume="+source+":"+dest+":rw" for source,dest in systemDirs.items()]),
     ("graphics-card", lambda p: ["--device=/dev/dri/"+device for device in os.listdir("/dev/dri")] + ["--volume=/dev/dri/:/dev/dri/:ro"] if p else []),
     ("serial-devices", lambda sd: ["--device=/dev/"+device for device in self.getSerialDevices()] if sd else []),
     ("system-dbus", lambda dbus: ["--volume=/var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket:rw"] if dbus else []),
     ("as-root", lambda root: ["--user=0"] if root else ["-e","USER="+self.getUser().getEndUser().name,"--user="+str(self.getUser().getEndUser().uid)]),
     # Anarchistic permissions
     ("run-commands-on-host", lambda p : ["--volume",self.getExecutionSpoolDir()+":/subuser/execute:rw"] if p else []),
     ("privileged", lambda p: ["--privileged"] if p else [])])

  def getExecutionSpoolDir(self):
    return os.path.join(self.getUser().getConfig()["volumes-dir"],"execute",str(os.getpid()))

  def getExecutionSpool(self):
    return os.path.join(self.getExecutionSpoolDir(),"spool")

  def setupExecutionSpool(self):
    try:
      shutil.rmtree(self.getExecutionSpoolDir())
    except (OSError,IOError):
      pass
    try:
      self.getUser().getEndUser().makedirs(os.path.join(self.getExecutionSpoolDir()))
    except (OSError,IOError):
      pass
    os.mkfifo(self.getExecutionSpool())
    executionSpoolReader = os.path.join(getSubuserDir(),"logic","execute-json-from-fifo")
    if not os.path.exists(executionSpoolReader):
      executionSpoolReader = subuserlib.executablePath.which("execute-json-from-fifo")
    self.__executionSpoolReader = self.getUser().getEndUser().Popen([executionSpoolReader,self.getExecutionSpool()],cwd=self.getExecutionSpoolDir())

  def tearDownExecutionSpool(self):
    self.__executionSpoolReader.terminate()
    shutil.rmtree(self.getExecutionSpoolDir())

  def setEnvVar(self,envVar,value):
    self.__extraFlags.append("-e")
    self.__extraFlags.append(envVar+"="+value)

  def setHostname(self,hostname):
    self.__hostname = hostname

  def getHostname(self):
    return self.__hostname

  def getHostnameFlag(self):
    if not self.__hostname is None:
      return ["--hostname",self.__hostname]
    else:
      return []

  def getCommand(self,args):
    """
    Returns the command required to run the subuser as a list of string arguments.
    """
    flags = self.getBasicFlags()
    flags.extend(self.__extraFlags)
    permissionFlagDict = self.getPermissionFlagDict()
    permissions = self.getSubuser().getPermissions()
    for permission, flagGenerator in permissionFlagDict.items():
      flags.extend(flagGenerator(permissions[permission]))
    flags.extend(self.getHostnameFlag())
    return ["run"]+flags+["--entrypoint"]+[self.entrypoint]+[self.getRunReadyImageId()]+args

  def getPrettyCommand(self,args):
    """
    Get a command for pretty printing for use with dry-run.
    """
    command = self.getCommand(args)
    return "docker '"+"' '".join(command)+"'"

  def getBackground(self):
    return self.__background

  def setBackground(self,background):
    self.__background = background

  def getBackgroundSuppressOutput(self):
    return self.__backgroundSuppressOutput

  def getBackgroundCollectOutput(self):
    return (self.__backgroundCollectStdout, self.__backgroundCollectStderr)

  def setBackgroundSuppressOutput(self,suppressOutput):
    self.__backgroundSuppressOutput = suppressOutput

  def setBackgroundCollectOutput(self,collectStdout,collectStderr):
    self.__backgroundCollectStdout = collectStdout
    self.__backgroundCollectStderr = collectStderr

  def getXautorityDirPath(self):
    return os.path.join(self.getUser().getConfig()["volumes-dir"],"x11",str(os.getpid()),self.getSubuser().getName())

  def getXautorityFilePath(self):
    return os.path.join(self.getXautorityDirPath(),".Xauthority")

  def setupXauth(self):
    try:
      self.getUser().getEndUser().makedirs(self.getXautorityDirPath())
    except OSError: #Already exists
      pass
    try:
      os.remove(self.getXautorityFilePath())
    except OSError:
      pass
    self.getUser().getEndUser().call(["xauth","extract",".Xauthority",self.getEnvvar("DISPLAY")],cwd=self.getXautorityDirPath())
    with open(self.getXautorityFilePath(),"rb") as xauthFile:
      # The extracted Xauthority file has the following format(bytewise):
      # 1 0 0 [len(hostname)] [hostname-in-ascii] 0 1 [display-number-in-ascii] 0 22 ["MIT-MAGIC-COOKIE-1"-in-ascii] 0 20 [Magic number]
      # The goal here, is to change the hostname...
      # BTW, either I am doing this totally wrong,
      # or python is terrible at dealing with binary files...
      start=xauthFile.read(3)
      lengthOfHostname = struct.unpack("b",xauthFile.read(1))[0]
      hostnameOfHost = xauthFile.read(lengthOfHostname)
      rest = xauthFile.read()
    with open(self.getXautorityFilePath(),"wb") as xauthFile:
      xauthFile.write(start)
      hostname = self.getHostname()
      hostname = hostname.encode("ascii")
      xauthFile.write(struct.pack("b",len(hostname)))
      xauthFile.write(hostname)
      xauthFile.write(rest)

  def run(self,args):
    """
    Run the subuser in a container.
    If the subuser is set to run in the background, return a docker Container object and the subprocess.
    Otherwise return the subuser's exit code.
    """
    def reallyRun():
      if not self.entrypoint:
        sys.exit("Cannot run subuser, no executable configured in permissions.json file.")
      if self.getSubuser().getPermissions()["stateful-home"]:
        self.getUser().getRegistry().log("Setting up subuser home dir.",verbosityLevel=4)
        self.getSubuser().setupHomeDir()
      if self.getSubuser().getPermissions()["stateful-home"] and self.getSubuser().getPermissions()["user-dirs"]:
        self.getUser().getRegistry().log("Creating user dir symlinks in subuser home dir.",verbosityLevel=4)
        userDirsDir = os.path.join(self.getSubuser().getHomeDirOnHost(),"Userdirs")
        if os.path.islink(userDirsDir):
          sys.exit("Please remove the old Userdirs directory, it is no longer needed. The path is:"+userDirsDir)
      if self.getSubuser().getPermissions()["x11"]:
        self.getUser().getRegistry().log("Generating xauth file.",verbosityLevel=4)
        self.setupXauth()
      if self.getSubuser().getPermissions()["run-commands-on-host"]:
        self.getUser().getRegistry().log("Launching execution spool daemon.",verbosityLevel=4)
        self.setupExecutionSpool()
      if self.getBackground():
        try:
          os.remove(self.getCidFile())
        except OSError:
          pass
      #Note, subusers with gui permission cannot be run in the background.
      # Make sure that everything is setup and ready to go.
      if not self.getSubuser().getPermissions()["gui"] is None:
        self.getUser().getRegistry().log("Requesting connection to X11 bridge.",verbosityLevel=4)
        self.getSubuser().getX11Bridge().addClient()
      self.getUser().getRegistry().log("Building run command.",verbosityLevel=4)
      command = self.getCommand(args)
      (collectStdout,collectStderr) = self.getBackgroundCollectOutput()
      self.getUser().getRegistry().log("Running subuser with Docker.",verbosityLevel=4)
      self.getUser().getRegistry().log(self.getPrettyCommand(args),verbosityLevel=4)
      returnValue = self.getUser().getDockerDaemon().execute(command,background=self.getBackground(),backgroundSuppressOutput=self.getBackgroundSuppressOutput(),backgroundCollectStdout=collectStdout,backgroundCollectStderr=collectStderr)
      if self.getSubuser().getPermissions()["run-commands-on-host"]:
        self.getUser().getRegistry().log("Stopping execution spool.",verbosityLevel=4)
        self.tearDownExecutionSpool()
      if not self.getSubuser().getPermissions()["gui"] is None:
        self.getUser().getRegistry().log("Disconnecting from X11 bridge.",verbosityLevel=4)
        self.getSubuser().getX11Bridge().removeClient()
      if self.getBackground():
        self.getUser().getRegistry().log("Waiting for CID file to be generated.",verbosityLevel=4)
        while not os.path.exists(self.getCidFile()) or os.path.getsize(self.getCidFile()) == 0:
          time.sleep(0.05)
        with open(self.getCidFile(),"r") as cidFile:
          self.getUser().getRegistry().log("Reading CID file.",verbosityLevel=4)
          containerId = cidFile.read()
          container = self.getUser().getDockerDaemon().getContainer(containerId)
          if container is None:
            sys.exit("Container failed to start:"+containerId)
          os.remove(self.getCidFile())
          return (container, returnValue)
      else:
        return returnValue
    #try:
    return reallyRun()
    #except KeyboardInterrupt:
    #  sys.exit(0)
