# -*- coding: utf-8 -*-

"""
An x11 bridge provides a secure/firewalled link between a desktop application and the host x11 server. In this case, we use XPRA to do the bridging.

::.

  -------------                      -------------
  |desktop app| <--/tmp/.X11-unix--> |xpra server|    Untrusted
  -------------                      -------------
                                           ^
                                           | ~/.xpra
                                           v
  -------------                       -------------
  | host      |  <--/tmp/.X11-unix--> |xpra client|   Trusted
  -------------                       -------------

This configuration involves 3 containers.

1) contains the untrusted desktop application
2) contains an untrusted xpra server
3) contains a trusted xpra client

I up-to-date version of xpra can be used, xpra need not be installed on the host.

"""

#external imports
import os
import time
import shutil
import errno
import sys
import hashlib
#internal imports
from subuserlib.classes.service import Service
from collections import OrderedDict
import subuserlib.verify
import subuserlib.subuser

class XpraX11Bridge(Service):
  def __init__(self,user,subuser):
    self.subuser = subuser
    Service.__init__(self,user,subuser)
    self.name = "xpra"

  def isSetup(self):
    clientSubuserInstalled = self.getClientSubuserName() in self.user.registry.subusers
    serverSubuserInstalled = self.getServerSubuserName() in self.user.registry.subusers
    return clientSubuserInstalled and serverSubuserInstalled

  def getSubuserSpecificServerPermissions(self):
    """
    Get the dictionary of permissions that are specific to this particular subuser and therefore are not packaged in the xpra server image source.
    """
    permissions = OrderedDict()
    permissions["system-dirs"] = OrderedDict(
                  [ (self.getXpraHomeDir(),"/home/subuser")
                  , (self.getServerSideX11Path(),"/tmp/.X11-unix") ])
    return permissions

  def getSubuserSpecificClientPermissions(self):
    """
    Get the dictionary of permissions that are specific to this particular subuser and therefore are not packaged in the xpra client image source.
    """
    permissions = OrderedDict()
    permissions["system-dirs"] = OrderedDict(
      [ (self.getXpraSocket()
        ,os.path.join(self.getClientSubuser().dockersideHome,".xpra","server-100"))
      , (self.getXpraTmpDir()
        ,os.path.join(self.getClientSubuser().dockersideHome,"tmp"))])
    return permissions

  def setupServerPermissions(self):
    permissions = self.getServerSubuser().permissions
    for key,value in self.getSubuserSpecificServerPermissions().items():
      permissions[key] = value
    permissions.save()

  def setupClientPermissions(self):
    permissions = self.getClientSubuser().permissions
    for key,value in self.getSubuserSpecificClientPermissions().items():
      permissions[key] = value
    permissions.save()

  def arePermissionsUpToDate(self):
    areClientPermissionsUpToDate = isSubDict(self.getSubuserSpecificClientPermissions(),self.getClientSubuser().permissions)
    if not areClientPermissionsUpToDate:
      self.user.registry.log("Client permissions:\n"+str(self.getClientSubuser().permissions)+ "\n differ from defaults:\n"+str(self.getSubuserSpecificClientPermissions()),verbosityLevel=4)
    areServerPermissionsUpToDate = isSubDict(self.getSubuserSpecificServerPermissions(),self.getServerSubuser().permissions)
    if not areServerPermissionsUpToDate:
      self.user.registry.log("Server permissions:\n"+str(self.getServerSubuser().permissions)+ "\n differ from defaults:\n"+str(self.getSubuserSpecificServerPermissions()),verbosityLevel=4)
    return areClientPermissionsUpToDate and areServerPermissionsUpToDate

  def setup(self):
    """
    Do any setup required in order to create a functional bridge: Creating subusers building images ect.
    """
    self.user.registry.log("Ensuring x11 bridge setup for subuser "+self.subuser.name,verbosityLevel=5)
    newSubuserNames = []
    if not self.isSetup():
      self.addServerSubuser()
      self.addClientSubuser()
      newSubuserNames = [self.getServerSubuserName(),self.getClientSubuserName()]
    if not self.arePermissionsUpToDate():
      self.user.registry.log("Updating x11 bridge permissions for subuser "+self.subuser.name,verbosityLevel=4)
      self.setupServerPermissions()
      self.setupClientPermissions()
      newSubuserNames = [self.getServerSubuserName(),self.getClientSubuserName()]
    newSubusers = []
    for newSubuserName in newSubuserNames:
      newSubusers.append(self.user.registry.subusers[newSubuserName])
    return newSubusers

  def getXpraVolumePath(self):
    return os.path.join(self.user.config["volumes-dir"],"xpra",self.subuser.name)

  def getServerSideX11Path(self):
    return os.path.join(self.getXpraVolumePath(),"tmp",".X11-unix")

  def getXpraHomeDir(self):
    return os.path.join(self.getXpraVolumePath(),"xpra-home")

  def getXpraTmpDir(self):
    return os.path.join(self.getXpraHomeDir(),"tmp")

  def getXpraSocket(self):
    return os.path.join(self.getXpraHomeDir(),".xpra",self.getServerSubuserHostname()+"-100")

  def getServerSubuserHostname(self):
    longHostName = "xpra-server"+hashlib.sha256(self.subuser.name.encode("utf-8")).hexdigest()
    return longHostName[:63]

  def getServerSubuserName(self):
    return "!service-subuser-"+self.subuser.name+"-xpra-server"

  def getServerSubuser(self):
    return self.user.registry.subusers[self.getServerSubuserName()]

  def _getPermissionsAccepter(self):
    from subuserlib.classes.permissionsAccepters.acceptPermissionsAtCLI import AcceptPermissionsAtCLI
    return AcceptPermissionsAtCLI(self.user,alwaysAccept=True)

  def addServerSubuser(self):
    try:
      subuserlib.subuser.addFromImageSourceNoVerify(self.user,self.getServerSubuserName(),self.user.registry.repositories["default"]["subuser-internal-xpra-server"])
    except KeyError:
      sys.exit("Your default repository does not provide a subuser-internal-xpra-server. This means we cannot use the xpra-x11 bridge. Please fix the default repository or file a bug report.")
    self.subuser.serviceSubuserNames.append(self.getServerSubuserName())
    self.getServerSubuser().createPermissions(self.getServerSubuser().imageSource.permissions)

  def getClientSubuserName(self):
    return "!service-subuser-"+self.subuser.name+"-xpra-client"

  def getClientSubuser(self):
    return self.user.registry.subusers[self.getClientSubuserName()]

  def addClientSubuser(self):
    subuserlib.subuser.addFromImageSourceNoVerify(self.user,self.getClientSubuserName(),self.user.registry.repositories["default"]["subuser-internal-xpra-client"])
    self.subuser.serviceSubuserNames.append(self.getClientSubuserName())
    self.getClientSubuser().createPermissions(self.getClientSubuser().imageSource.permissions)

  def cleanUp(self):
    """
    Clear special volumes. This ensures statelessness of stateless subusers.
    """
    self.user.registry.log("Cleaning up old bridge volume files.",verbosityLevel=4)
    try:
      shutil.rmtree(os.path.join(self.user.config["volumes-dir"],"xpra",self.subuser.name))
    except OSError as e:
      # We need to clean this up.
      # Unfortunately, the X11 socket may still exist and will be owned by root.
      # So we cannot do the clean up as a normal user.
      # Fortunately, being a member of the docker group is the same as having root access.
      if not e.errno == errno.ENOENT:
        self.user.registry.log("An error occured while setting up xpra X11 socket.",verbosityLevel=3)
        self.user.registry.log(str(e),verbosityLevel=3)
        self.user.dockerDaemon.execute(["run","--rm","--volume",os.path.join(self.user.config["volumes-dir"],"xpra")+":/xpra-volume","--entrypoint","/bin/rm",self.getServerSubuser().imageId,"-rf",os.path.join("/xpra-volume/",self.subuser.name)])

  def createAndSetupSpecialVolumes(self,errorCount=0):
    def clearAndTryAgain():
      if errorCount >= 5:
        sys.exit("Failed to setup XPRA bridge volumes. You have some permissions errors with your subuser volumes directory."+self.getXpraVolumePath()+" Look at the output above and try to resolve the problem yourself. Possible causes are simple ownership problems, apparmor, SELinux. If you fail to find a simple explanation for your permissions problems. Please file a bug report.")
      self.cleanUp()
      self.createAndSetupSpecialVolumes(errorCount=errorCount+1)
    def mkdirs(directory):
      self.user.registry.log("Creating the "+directory+" directory.",verbosityLevel=4)
      try:
        self.user.endUser.makedirs(directory)
      except OSError as e:
        if e.errno == errno.EEXIST or e.errno == errno.EACCES:
          self.user.registry.log(str(e),verbosityLevel=3)
          self.user.registry.log("Clearing xpra X11 socket.",verbosityLevel=3)
          clearAndTryAgain()
        else:
          raise e
    self.user.registry.log("Setting up XPRA bridge volumes.",verbosityLevel=4)
    mkdirs(self.getServerSideX11Path())
    mkdirs(self.getXpraHomeDir())
    mkdirs(self.getXpraTmpDir())
    try:
      os.chmod(self.getServerSideX11Path(),1023)
    except OSError as e:
      if e.errno == errno.EPERM:
        self.user.registry.log("X11 bridge perm error, clearing a trying again.")
        clearAndTryAgain()

  def start(self,serviceStatus):
    """
    Start the bridge.
    """
    if not self.arePermissionsUpToDate():
      sys.exit("The configuration of the xpra bridge has changed in a recent version. You must update the xpra bridge configuration by running\n\n$subuser repair")
    self.cleanUp()
    self.createAndSetupSpecialVolumes()
    permissionDict = {
     "system-tray": ("--system-tray" , "--no-system-tray"),
     "cursors": ("--cursors", "--no-cursors"),
     "clipboard": ("--clipboard","--no-clipboard")}
    permissionArgs = []
    for guiPermission,(on,off) in permissionDict.items():
      if self.subuser.permissions["gui"][guiPermission]:
        permissionArgs.append(on)
      else:
        permissionArgs.append(off)
    commonArgs = ["--no-daemon", "--no-notifications", "--mmap", "--opengl=no"]
    commonEnvVars = { "XPRA_CLIPBOARD_LIMIT" : "45"
                    , "XPRA_CLIPBOARDS"      : "CLIPBOARD" }
    # Launch xpra server
    serverArgs = ["start","--no-pulseaudio","--no-mdns","--encoding=rgb"]
    suppressOutput = not "SUBUSER_DEBUG_XPRA" in os.environ
    serverArgs.extend(commonArgs)
    serverArgs.extend(permissionArgs)
    serverArgs.append(":100")
    serverRuntime = self.getServerSubuser().getRuntime(os.environ)
    serverRuntime.logIfInteractive("Starting xpra server...")
    serverRuntime.hostname = self.getServerSubuserHostname()
    self.user.registry.log("Hostname set.",verbosityLevel=4)
    serverRuntime.setEnvVar("TMPDIR",os.path.join("/home/subuser","tmp"))
    for arg, value in commonEnvVars.items():
      serverRuntime.setEnvVar(arg, value)
    serverRuntime.background = True
    serverRuntime.backgroundSuppressOutput = suppressOutput
    serverRuntime.setBackgroundCollectOutput(False,True)
    self.user.registry.log("Entering run subrutine.",verbosityLevel=4)
    (serverContainer, serverProcess) = serverRuntime.run(args=serverArgs)
    self.user.registry.log("Getting server CID",verbosityLevel=4)
    serviceStatus["xpra-server-service-cid"] = serverContainer.id
    self.waitForContainerToLaunch("xpra is ready", serverProcess, suppressOutput)
    # Launch xpra client
    try:
      borderColor = self.subuser.permissions["gui"]["border-color"]
      if "-" in borderColor:
        borderColor = "red"
    except:
      borderColor = "red"
    clientArgs = ["attach","--no-tray","--compress=0","--encoding=rgb","--border",borderColor]
    clientArgs.extend(commonArgs)
    clientArgs.extend(permissionArgs)
    clientRuntime = self.getClientSubuser().getRuntime(os.environ)
    clientRuntime.logIfInteractive("Starting xpra client...")
    clientRuntime.setEnvVar("XPRA_SOCKET_HOSTNAME","server")
    clientRuntime.setEnvVar("TMPDIR",os.path.join("/home/subuser","tmp"))
    for arg, value in commonEnvVars.items():
      clientRuntime.setEnvVar(arg, value)
    clientRuntime.background = True
    clientRuntime.backgroundSuppressOutput = suppressOutput
    (clientContainer, clientProcess) = clientRuntime.run(args=clientArgs)
    serviceStatus["xpra-client-service-cid"] = clientContainer.id
    return serviceStatus

  def waitForContainerToLaunch(self, readyString, process, suppressOutput):
    while True:
      where = process.stderr_file.tell()
      line = process.stderr_file.readline()
      while (not line):# or (line[-1:] != '\n'):
        time.sleep(0.1)
        process.stderr_file.seek(where)
        line = process.stderr_file.readline()
      if not suppressOutput:
        subuserlib.print.printWithoutCrashing(line[:-1])
      if readyString in line:
        break
    process.stderr_file.close()

  def stop(self,serviceStatus):
    """
    Stop the bridge.
    """
    self.user.dockerDaemon.getContainer(serviceStatus["xpra-client-service-cid"]).stop()
    self.user.dockerDaemon.getContainer(serviceStatus["xpra-server-service-cid"]).stop()
    if not "SUBUSER_DEBUG_XPRA" in os.environ:
      self.cleanUp()

  def isRunning(self,serviceStatus):
    def isContainerRunning(cid):
      container = self.user.dockerDaemon.getContainer(cid)
      containerStatus = container.inspect()
      if containerStatus is None:
        return False
      else:
        if not containerStatus["State"]["Running"]:
          #Clean up left over container
          container.remove(force=True)
          return False
        else:
          return True
    return isContainerRunning(serviceStatus["xpra-client-service-cid"]) and isContainerRunning(serviceStatus["xpra-server-service-cid"])

def X11Bridge(user,subuser):
  return bridges[user.config["x11-bridge"]](user,subuser)

bridges = {"xpra":XpraX11Bridge}

########################################################################
# Helper functions

def isSubDict(subDict,dictionary):
  for key in subDict.keys():
    if (not key in dictionary) or (not subDict[key] == dictionary[key]):
      if (key in dictionary) and (type(subDict[key]) == type(dictionary[key]) == OrderedDict):
        for innerDictKey in subDict[key].keys():
          if not innerDictKey in dictionary[key]:
            pass
          elif not subDict[key][innerDictKey] == dictionary[key][innerDictKey]:
            print(key+"."+innerDictKey+"  "+str(subDict[key][innerDictKey])+" != "+str(dictionary[key][innerDictKey]))
      return False
  return True
