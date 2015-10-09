#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

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
#internal imports
from subuserlib.classes.service import Service
import subuserlib.verify
import subuserlib.subuser

class XpraX11Bridge(Service):
  def __init__(self,user,subuser):
    self.__subuser = subuser
    Service.__init__(self,user,subuser)

  def getName(self):
    return "xpra"

  def getSubuser(self):
    return self.__subuser

  def isSetup(self):
    clientSubuserInstalled = self.getClientSubuserName() in self.getUser().getRegistry().getSubusers()
    serverSubuserInstalled = self.getServerSubuserName() in self.getUser().getRegistry().getSubusers()
    return clientSubuserInstalled and serverSubuserInstalled

  def getSubuserSpecificServerPermissions(self):
    """
    Get the dictionary of permissions that are specific to this particular subuser and therefore are not packaged in the xpra server image source.
    """
    permissions = {}
    permissions["system-dirs"] = {self.getServerSideX11Path():"/tmp/.X11-unix",self.getXpraHomeDir():self.getUser().getEndUser().homeDir}
    return permissions

  def getSubuserSpecificClientPermissions(self):
    """
    Get the dictionary of permissions that are specific to this particular subuser and therefore are not packaged in the xpra client image source.
    """
    permissions = {}
    permissions["system-dirs"] = {self.getXpraSocket():os.path.join(self.getClientSubuser().getDockersideHome(),".xpra","server-100"),self.getXpraTmpDir():os.path.join(self.getClientSubuser().getDockersideHome(),"tmp")}
    return permissions

  def setupServerPermissions(self):
    permissions = self.getServerSubuser().getPermissions()
    for key,value in self.getSubuserSpecificServerPermissions().items():
      permissions[key] = value
    permissions.save()

  def setupClientPermissions(self):
    permissions = self.getClientSubuser().getPermissions()
    for key,value in self.getSubuserSpecificClientPermissions().items():
      permissions[key] = value
    permissions.save()

  def arePermissionsUpToDate(self):
    areClientPermissionsUpToDate = isSubDict(self.getSubuserSpecificClientPermissions(),self.getClientSubuser().getPermissions())
    areServerPermissionsUpToDate = isSubDict(self.getSubuserSpecificServerPermissions(),self.getServerSubuser().getPermissions())
    return areClientPermissionsUpToDate and areServerPermissionsUpToDate

  def setup(self):
    """
    Do any setup required in order to create a functional bridge: Creating subusers building images ect.
    """
    newSubuserNames = []
    if not self.isSetup():
      self.addServerSubuser()
      self.addClientSubuser()
      newSubuserNames = [self.getServerSubuserName(),self.getClientSubuserName()]
    if not self.arePermissionsUpToDate():
      self.setupServerPermissions()
      self.setupClientPermissions()
      newSubuserNames = [self.getServerSubuserName(),self.getClientSubuserName()]
    return newSubuserNames

  def getXpraVolumePath(self):
    return os.path.join(self.getUser().getConfig()["volumes-dir"],"xpra",self.getSubuser().getName())

  def getServerSideX11Path(self):
    return os.path.join(self.getXpraVolumePath(),"tmp",".X11-unix")

  def getXpraHomeDir(self):
    return os.path.join(self.getXpraVolumePath(),"xpra-home")

  def getXpraTmpDir(self):
    return os.path.join(self.getXpraHomeDir(),"tmp")

  def getXpraSocket(self):
    return os.path.join(self.getXpraHomeDir(),".xpra",self.getServerSubuserHostname()+"-100")

  def getServerSubuserHostname(self):
    return "service-subuser-"+self.getSubuser().getName()+"-xpra-server"

  def getServerSubuserName(self):
    return "!"+self.getServerSubuserHostname()

  def getServerSubuser(self):
    return self.getUser().getRegistry().getSubusers()[self.getServerSubuserName()]

  def _getPermissionsAccepter(self):
    from subuserlib.classes.permissionsAccepters.acceptPermissionsAtCLI import AcceptPermissionsAtCLI
    return AcceptPermissionsAtCLI(self.getUser(),alwaysAccept=True)

  def addServerSubuser(self):
    subuserlib.subuser.addFromImageSourceNoVerify(self.getUser(),self.getServerSubuserName(),self.getUser().getRegistry().getRepositories()["default"]["subuser-internal-xpra-server"])
    self.getSubuser().addServiceSubuser(self.getServerSubuserName())
    self.getServerSubuser().createPermissions(self.getServerSubuser().getImageSource().getPermissions())

  def getClientSubuserName(self):
    return "!service-subuser-"+self.getSubuser().getName()+"-xpra-client"

  def getClientSubuser(self):
    return self.getUser().getRegistry().getSubusers()[self.getClientSubuserName()]

  def addClientSubuser(self):
    subuserlib.subuser.addFromImageSourceNoVerify(self.getUser(),self.getClientSubuserName(),self.getUser().getRegistry().getRepositories()["default"]["subuser-internal-xpra-client"])
    self.getSubuser().addServiceSubuser(self.getClientSubuserName())
    self.getClientSubuser().createPermissions(self.getClientSubuser().getImageSource().getPermissions())

  def cleanUp(self):
    """
    Clear special volumes. This ensures statelessness of stateless subusers.
    """
    try:
      shutil.rmtree(os.path.join(self.getUser().getConfig()["volumes-dir"],"xpra",self.getSubuser().getName()))
    except OSError:
      pass

  def createAndSetupSpecialVolumes(self):
    def clearAndTryAgain():
      # We need to clean this up.
      # Unfortunately, the X11 socket will be owned by root.
      # So we cannot do the clean up as a normal user.
      # Fortunately, being a member of the docker group is the same as having root access.
      self.getUser().getDockerDaemon().execute(["run","--rm","--volume",os.path.join(self.getUser().getConfig()["volumes-dir"],"xpra")+":/xpra-volume","--entrypoint","/bin/rm",self.getServerSubuser().getImageId(),"-rf",os.path.join("/xpra-volume/",self.getSubuser().getName())])
      # Having preformed our clean up steps, we try again.
      self.createAndSetupSpecialVolumes()
    def mkdirs(directory):
      try:
        self.getUser().getEndUser().makedirs(directory)
      except OSError as e:
        if e.errno == errno.EEXIST or e.errno == errno.EACCES:
          clearAndTryAgain()
        else:
          raise e
    mkdirs(self.getServerSideX11Path())
    mkdirs(self.getXpraHomeDir())
    mkdirs(self.getXpraTmpDir())
    try:
      os.chmod(self.getServerSideX11Path(),1023)
    except OSError as e:
      if e.errno == errno.EPERM:
        print("X11 bridge perm error, clearing a trying again.")
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
      if self.getSubuser().getPermissions()["gui"][guiPermission]:
        permissionArgs.append(on)
      else:
        permissionArgs.append(off)
    commonArgs = ["--no-daemon","--no-notifications","--mmap"]
    # Launch xpra server
    serverArgs = ["start","--no-pulseaudio","--no-mdns","--encoding=rgb"]
    suppressOutput = not "SUBUSER_DEBUG_XPRA" in os.environ
    serverArgs.extend(commonArgs)
    serverArgs.extend(permissionArgs)
    serverArgs.append(":100")
    serverRuntime = self.getServerSubuser().getRuntime(os.environ)
    serverRuntime.logIfInteractive("Starting xpra server...")
    serverRuntime.setHostname(self.getServerSubuserHostname())
    serverRuntime.setEnvVar("TMPDIR",os.path.join(self.getUser().getEndUser().homeDir,"tmp"))
    serverRuntime.setBackground(True)
    serverRuntime.setBackgroundSuppressOutput(suppressOutput)
    serverRuntime.setBackgroundCollectOutput(False,True)
    (serverContainer, serverProcess) = serverRuntime.run(args=serverArgs)
    serviceStatus["xpra-server-service-cid"] = serverContainer.getId()
    self.waitForContainerToLaunch("xpra is ready", serverProcess, suppressOutput)
    # Launch xpra client
    clientArgs = ["attach","--no-tray","--compress=0","--encoding=rgb"]
    clientArgs.extend(commonArgs)
    clientArgs.extend(permissionArgs)
    clientRuntime = self.getClientSubuser().getRuntime(os.environ)
    clientRuntime.logIfInteractive("Starting xpra client...")
    clientRuntime.setEnvVar("XPRA_SOCKET_HOSTNAME","server")
    clientRuntime.setEnvVar("TMPDIR",os.path.join(self.getUser().getEndUser().homeDir,"tmp"))
    clientRuntime.setBackground(True)
    clientRuntime.setBackgroundSuppressOutput(suppressOutput)
    (clientContainer, clientProcess) = clientRuntime.run(args=clientArgs)
    serviceStatus["xpra-client-service-cid"] = clientContainer.getId()
    return serviceStatus

  def waitForContainerToLaunch(self, readyString, process, suppressOutput):
    while True:
      where = process.stderr_file.tell()
      line = process.stderr_file.readline()
      if (not line) or (line[-1:] != '\n'):
        time.sleep(0.1)
        process.stderr_file.seek(where)
      else:
        if not suppressOutput:
          print(line[:-1])
        if readyString in line:
          break
    process.stderr_file.close()

  def stop(self,serviceStatus):
    """
    Stop the bridge.
    """
    self.getUser().getDockerDaemon().getContainer(serviceStatus["xpra-client-service-cid"]).stop()
    self.getUser().getDockerDaemon().getContainer(serviceStatus["xpra-server-service-cid"]).stop()
    if not "SUBUSER_DEBUG_XPRA" in os.environ:
      self.cleanUp()

  def isRunning(self,serviceStatus):
    def isContainerRunning(cid):
      container = self.getUser().getDockerDaemon().getContainer(cid)
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
  return bridges[user.getConfig()["x11-bridge"]](user,subuser)

bridges = {"xpra":XpraX11Bridge}

########################################################################
# Helper functions

def isSubDict(subDict,dictionary):
  for key in subDict.keys():
    if (not key in dictionary) or (not subDict[key] == dictionary[key]):
      return False
  return True
