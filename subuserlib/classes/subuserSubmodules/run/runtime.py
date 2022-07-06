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
    self.subuser = subuser
    self.env = environment
    self.backgroundSuppressOutput = True
    self.__backgroundCollectStdout = False
    self.__backgroundCollectStderr = False
    self.__executionSpoolReader = None
    if extraDockerFlags is None:
      self.__extraFlags = []
    else:
      self.__extraFlags = extraDockerFlags
    if not entrypoint:
      self.entrypoint = self.subuser.permissions["executable"]
    else:
      self.entrypoint = entrypoint
    self.background = False
    if not subuserlib.test.testing:
      self.hostname = binascii.b2a_hex(os.urandom(10)).decode()
    else:
      self.hostname = "<random-hostname>"
    UserOwnedObject.__init__(self,user)

  def getRunReadyImageId(self):
    try:
      image = self.subuser.getRunReadyImage().id
      if image is None:
        raise KeyError()
      else:
        return image
    except KeyError:
      sys.exit("""No run ready image is prepaired for this subuser. Please run:

$ subuser repair
""")

  def getEnvvar(self,var):
    try:
      return self.env[var]
    except KeyError:
      sys.exit("The env var %s is not set. Are you sure you are running as a normal user?" % var)

  def getSerialDevices(self):
    return [device for device in os.listdir("/dev/") if device.startswith("ttyS") or device.startswith("ttyUSB") or device.startswith("ttyACM")]

  def getGraphicsCardDevices(self):
    try:
      return [device for device in os.listdir("/dev/dri") if not os.path.isdir(os.path.join("/dev/dri", device))]
    except FileNotFoundError as e:
      if subuserlib.test.testing:
        return ["card0","controlD64"]
      else:
        system.exit("No graphics card available. /dev/dri does not exist.")

  def getCidFile(self):
    return "/tmp/subuser-"+self.subuser.name

  def prepUserDir(self,userDir):
    pathOnHost = os.path.join(self.subuser.user.endUser.homeDir,userDir)
    if not os.path.exists(pathOnHost):
      self.user.endUser.makedirs(pathOnHost)
    return pathOnHost

  def getBasicFlags(self):
    common = ["--rm"]
    if self.background:
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
      return ["-e",envVar+"="+self.env[envVar]]
    except KeyError:
      return []

  def getSoundCardArgs(self):
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

  def getPulseAudioArgs(self):
    if "PULSE_SERVER" in self.env:
      pulseSocket = self.env["PULSE_SERVER"]
    else:
      try:
          pactl_output = self.user.endUser.callCollectOutput(["pactl", "info"])
          if pactl_output[0] == 0:
              pulseSocket = next(filter(None, map(lambda x: x[20:] if x.startswith("Server String: unix:") else None, pactl_output[1].split('\n'))), None)
          else:
              pulseSocket = None
      except Exception as e:
          pulseSocket = None

    if "PULSE_COOKIE" in self.env:
      pulseCookieFile = self.env["PULSE_COOKIE"]
    else:
      pulseCookieFile = next((f for f in [os.path.join(self.user.endUser.homeDir, ".config", "pulse", "cookie"), os.path.join(self.user.endUser.homeDir,".pulse","cookie")] if os.path.exists(f)), None)
    if pulseSocket is not None and pulseCookieFile is not None:
      return ["--volume="+pulseCookieFile+":/subuser/pulse/cookie"
             ,"--volume="+pulseSocket+":/subuser/pulse/socket"
             ,"-e"
             ,"PULSE_COOKIE=/subuser/pulse/cookie"
             ,"-e"
             ,"PULSE_SERVER=/subuser/pulse/socket"]
    else:
      return []

  def getBasicCommonPermissionDict(self):
    return collections.OrderedDict([
        ("stateful-home", lambda p : ["--volume="+self.subuser.homeDirOnHost+":"+self.subuser.dockersideHome+":rw","-e","HOME="+self.subuser.dockersideHome] if p else ["-e","HOME="+self.subuser.dockersideHome]),
        ("inherit-locale", lambda p : self.passOnEnvVar("LANG")+self.passOnEnvVar("LANGUAGE") if p else []),
        ("inherit-timezone", lambda p : self.passOnEnvVar("TZ")+["--volume=/etc/localtime:/etc/localtime:ro"] if p else [])
      ])

  def getBasicCommonPermissionFlags(self,bcps):
    bcpd = self.getBasicCommonPermissionDict()

    flags = []
    for permission,flagGenerator in bcpd.items():
      if type(bcps) == collections.OrderedDict and permission in bcps:
        flags.extend(flagGenerator(bcps[permission]))
      else:
        flags.extend(flagGenerator(False))
    return flags

  def getPermissionFlagDict(self):
    """
    This is a dictionary mapping permissions to functions which when given the permission's values return docker run flags.
    """
    return collections.OrderedDict([
     # Conservative permissions
     ("basic-common-permissions", self.getBasicCommonPermissionFlags),
     ("memory-limit", lambda p: ["--memory="+str(p)] if p else []),
     ("max-cpus", lambda p: ["--cpus="+str(p)] if p else []),
     # Moderate permissions
     ("gui", lambda p : ["-e","DISPLAY=unix:100","--volume",self.subuser.x11Bridge.getServerSideX11Path()+":/tmp/.X11-unix:rw"] if p else []),
     ("user-dirs", lambda userDirs : ["--volume="+self.prepUserDir(userDir)+":"+os.path.join("/subuser/userdirs/",userDir)+":rw" for userDir in userDirs]),
     ("inherit-envvars", lambda envVars: [arg for var in envVars for arg in self.passOnEnvVar (var)]),
     ("sound-card", lambda p: self.getSoundCardArgs() if p else []),
     ("pulseaudio", lambda p: self.getPulseAudioArgs() if p else []),
     ("webcam", lambda p: ["--device=/dev/"+device for device in os.listdir("/dev/") if device.startswith("video")] if p else []),
     ("access-working-directory", lambda p: ["--volume="+os.getcwd()+":/pwd:rw","--workdir=/pwd"] if p else ["--workdir="+self.subuser.dockersideHome]),
     ("allow-network-access", lambda p: ["--net=bridge"] if p else ["--net=none"]),
     # Liberal permissions
     ("x11", lambda p: ["-e","DISPLAY=unix"+self.getEnvvar('DISPLAY'),"--volume=/tmp/.X11-unix:/tmp/.X11-unix:rw","--volume="+self.getXautorityFilePath()+":/subuser/.Xauthority:ro","-e","XAUTHORITY=/subuser/.Xauthority"] if p else []),
     ("system-dirs", lambda systemDirs : ["--volume="+source+":"+dest+":rw" for source,dest in systemDirs.items()]),
     ("graphics-card", lambda p: ["--device=/dev/dri/"+device for device in self.getGraphicsCardDevices()] + ["--volume=/dev/dri/:/dev/dri/:ro"] if p else []),
     ("serial-devices", lambda sd: ["--device=/dev/"+device for device in self.getSerialDevices()] if sd else []),
     ("system-dbus", lambda dbus: ["--volume=/var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket:rw"] if dbus else []),
     ("as-root", lambda root: ["--user=0"] if root else ["-e","USER=subuser","--user="+str(self.user.endUser.uid)]),
     # Anarchistic permissions
     ("run-commands-on-host", lambda p : ["--volume",self.getExecutionSpoolDir()+":/subuser/execute:rw"] if p else []),
     ("privileged", lambda p: ["--privileged"] if p else [])])

  def getExecutionSpoolDir(self):
    return os.path.join(self.user.config["volumes-dir"],"execute",str(os.getpid()))

  def getExecutionSpool(self):
    return os.path.join(self.getExecutionSpoolDir(),"spool")

  def setupExecutionSpool(self):
    try:
      shutil.rmtree(self.getExecutionSpoolDir())
    except (OSError,IOError):
      pass
    try:
      self.user.endUser.makedirs(os.path.join(self.getExecutionSpoolDir()))
    except (OSError,IOError):
      pass
    os.mkfifo(self.getExecutionSpool())
    executionSpoolReader = os.path.join(getSubuserDir(),"logic","execute-json-from-fifo")
    if not os.path.exists(executionSpoolReader):
      executionSpoolReader = subuserlib.executablePath.which("execute-json-from-fifo")
    self.__executionSpoolReader = self.user.endUser.Popen([executionSpoolReader,self.getExecutionSpool()],cwd=self.getExecutionSpoolDir())

  def tearDownExecutionSpool(self):
    self.__executionSpoolReader.terminate()
    shutil.rmtree(self.getExecutionSpoolDir())

  def setEnvVar(self,envVar,value):
    self.__extraFlags.append("-e")
    self.__extraFlags.append(envVar+"="+value)

  def getHostnameFlag(self):
    if not self.hostname is None:
      return ["--hostname",self.hostname]
    else:
      return []

  def getCommand(self,args):
    """
    Returns the command required to run the subuser as a list of string arguments.
    """
    flags = self.getBasicFlags()
    flags.extend(self.__extraFlags)
    permissionFlagDict = self.getPermissionFlagDict()
    permissions = self.subuser.permissions
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

  def getBackgroundCollectOutput(self):
    return (self.__backgroundCollectStdout, self.__backgroundCollectStderr)

  def setBackgroundCollectOutput(self,collectStdout,collectStderr):
    self.__backgroundCollectStdout = collectStdout
    self.__backgroundCollectStderr = collectStderr

  def getXautorityDirPath(self):
    return os.path.join(self.user.config["volumes-dir"],"x11",str(os.getpid()),self.subuser.name)

  def getXautorityFilePath(self):
    return os.path.join(self.getXautorityDirPath(),".Xauthority")

  def setupXauth(self):
    try:
      self.user.endUser.makedirs(self.getXautorityDirPath())
    except OSError: #Already exists
      pass
    try:
      os.remove(self.getXautorityFilePath())
    except OSError:
      pass
    self.user.endUser.call(["xauth","extract",".Xauthority",self.getEnvvar("DISPLAY")],cwd=self.getXautorityDirPath())
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
      hostname = self.hostname
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
      if self.subuser.permissions["basic-common-permissions"] and self.subuser.permissions["basic-common-permissions"]["stateful-home"]:
        self.user.registry.log("Setting up subuser home dir.",verbosityLevel=4)
        self.subuser.setupHomeDir()
        if self.subuser.permissions["user-dirs"]:
          self.user.registry.log("Creating user dir symlinks in subuser home dir.",verbosityLevel=4)
          userDirsDir = os.path.join(self.subuser.homeDirOnHost,"Userdirs")
          if os.path.islink(userDirsDir):
            sys.exit("Please remove the old Userdirs directory, it is no longer needed. The path is:"+userDirsDir)
      if self.subuser.permissions["x11"]:
        self.user.registry.log("Generating xauth file.",verbosityLevel=4)
        self.setupXauth()
      if self.subuser.permissions["run-commands-on-host"]:
        self.user.registry.log("Launching execution spool daemon.",verbosityLevel=4)
        self.setupExecutionSpool()
      if self.background:
        try:
          os.remove(self.getCidFile())
        except OSError:
          pass
      #Note, subusers with gui permission cannot be run in the background.
      # Make sure that everything is setup and ready to go.
      if self.subuser.permissions["gui"]:
        self.user.registry.log("Requesting connection to X11 bridge.",verbosityLevel=4)
        self.subuser.x11Bridge.addClient()
      self.user.registry.log("Building run command.",verbosityLevel=4)
      command = self.getCommand(args)
      (collectStdout,collectStderr) = self.getBackgroundCollectOutput()
      self.user.registry.log("Running subuser with Docker.",verbosityLevel=4)
      self.user.registry.log(self.getPrettyCommand(args),verbosityLevel=4)
      returnValue = self.user.dockerDaemon.execute(command,background=self.background,backgroundSuppressOutput=self.backgroundSuppressOutput,backgroundCollectStdout=collectStdout,backgroundCollectStderr=collectStderr)
      if self.subuser.permissions["run-commands-on-host"]:
        self.user.registry.log("Stopping execution spool.",verbosityLevel=4)
        self.tearDownExecutionSpool()
      if self.subuser.permissions["gui"]:
        self.user.registry.log("Disconnecting from X11 bridge.",verbosityLevel=4)
        self.subuser.x11Bridge.removeClient()
      if self.background:
        self.user.registry.log("Waiting for CID file to be generated.",verbosityLevel=4)
        while not os.path.exists(self.getCidFile()) or os.path.getsize(self.getCidFile()) == 0:
          time.sleep(0.05)
        with open(self.getCidFile(),"r") as cidFile:
          self.user.registry.log("Reading CID file.",verbosityLevel=4)
          containerId = cidFile.read()
          container = self.user.dockerDaemon.getContainer(containerId)
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

class DarwinRuntime(Runtime):
  def getBasicCommonPermissionDict(self):
    perms = super().getBasicCommonPermissionDict()
    if perms.pop("inherit-timezone", True):
      self.user.registry.log("Warning: inherit-timezone is set, but not supported on darwin.",verbosityLevel=4)
    return perms
