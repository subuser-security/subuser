#!/usr/bin/env python # This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
Contains code that prepairs a subuser to be run and then runs it.
"""

#external imports
import sys,os,getpass,collections
#internal imports
import subuserlib.subprocessExtras

def getRecursiveDirectoryContents(directory):
  files = []
  for (directory,_,fileList) in os.walk(directory):
    for fileName in fileList:
      files.append(os.path.join(directory,fileName))
  return files

def generateImagePreparationDockerfile(subuserToRun):
  """
  There is still some preparation that needs to be done before an image is ready to be run.  But this preparation requires run time information, so we cannot preform that preparation at build time.
  """
  dockerfileContents  = "FROM "+subuserToRun.getImageId()+"\n"
  dockerfileContents += "RUN useradd --uid="+str(os.getuid())+" "+getpass.getuser()+" ;export exitstatus=$? ; if [ $exitstatus -eq 4 ] ; then echo uid exists ; elif [ $exitstatus -eq 9 ]; then echo username exists. ; else exit $exitstatus ; fi\n"
  dockerfileContents += "RUN test -d /home/"+getpass.getuser()+" || mkdir /home/"+getpass.getuser()+" && chown "+getpass.getuser()+" /home/"+getpass.getuser()+"\n"
  if subuserToRun.getPermissions()["serial-devices"]:
    dockerfileContents += "RUN groupadd dialout; export exitstatus=$? ; if [ $exitstatus -eq 4 ] ; then echo gid exists ; elif [ $exitstatus -eq 9 ]; then echo groupname exists. ; else exit $exitstatus ; fi\n"
    dockerfileContents += "RUN groupadd uucp; export exitstatus=$? ; if [ $exitstatus -eq 4 ] ; then echo gid exists ; elif [ $exitstatus -eq 9 ]; then echo groupname exists. ; else exit $exitstatus ; fi\n"
    dockerfileContents += "RUN usermod -a -G dialout "+getpass.getuser()+"\n"
    dockerfileContents += "RUN usermod -a -G uucp "+getpass.getuser()+"\n"
  if subuserToRun.getPermissions()["sudo"]:
    dockerfileContents += "RUN (umask 337; echo \""+getpass.getuser()+" ALL=(ALL) NOPASSWD: ALL\" > /etc/sudoers.d/allowsudo )\n"
  return dockerfileContents

def buildRunReadyImageForSubuser(subuserToRun):
  """
  Returns the Id of the Docker image to be run.
  """
  try:
    imageId = subuserToRun.getUser().getDockerDaemon().build(None,quietClient=True,useCache=True,forceRm=False,rm=False,dockerfile=generateImagePreparationDockerfile(subuserToRun))
  except subuserlib.classes.dockerDaemon.ImageBuildException as ibe:
    sys.exit(str(ibe))
  return imageId

def getSerialDevices():
  return [device for device in os.listdir("/dev/") if device.startswith("ttyS") or device.startswith("ttyUSB") or device.startswith("ttyACM")]

def getBasicFlags():
  return [
    "-i",
    "-t",
    "--rm"]

def passOnEnvVar(envVar):
  """
  Generate the arguments required to pass on a given ENV var to the container from the host.
  """
  try:
    return ["-e",envVar+"="+os.environ[envVar]]
  except KeyError:
    return []

def generateSoundArgs():
  soundArgs = []
  if os.path.exists("/dev/snd"):
    soundArgs += ["--device=/dev/snd/"+device for device in os.listdir("/dev/snd") if not device == "by-id" and not device == "by-path"]
  if os.path.exists("/dev/dsp"):
    soundArgs += ["--device=/dev/dsp/"+device for device in os.listdir("/dev/dsp")]
  return soundArgs

def getPermissionFlagDict(subuserToRun):
  """
  This is a dictionary mapping permissions to functions which when given the permission's values return docker run flags.
  """
  return collections.OrderedDict([
   # Conservative permissions
   ("stateful-home", lambda p : ["-v="+subuserToRun.getHomeDirOnHost()+":"+subuserToRun.getDockersideHome()+":rw","-e","HOME="+subuserToRun.getDockersideHome()] if p else ["-e","HOME="+subuserToRun.getDockersideHome()]),
   ("inherit-locale", lambda p : passOnEnvVar("LANG")+passOnEnvVar("LANGUAGE") if p else []),
   ("inherit-timezone", lambda p : passOnEnvVar("TZ")+["-v=/etc/localtime:/etc/localtime:r"] if p else []),
   # Moderate permissions
   ("user-dirs", lambda userDirs : ["-v="+os.path.join(subuserToRun.getUser().homeDir,userDir)+":"+os.path.join("/userdirs/",userDir)+":rw" for userDir in userDirs]),
   ("sound-card", lambda p: generateSoundArgs() if p else []),
   ("webcam", lambda p: ["--device=/dev/"+device for device in os.listdir("/dev/") if device.startswith("video")] if p else []),
   ("access-working-directory", lambda p: ["-v="+os.getcwd()+":/pwd:rw","--workdir=/pwd"] if p else ["--workdir="+subuserToRun.getDockersideHome()]),
   ("allow-network-access", lambda p: ["--net=bridge","--dns=8.8.8.8"] if p else ["--net=none"]),
   # Liberal permissions
   ("x11", lambda p: ["-e","DISPLAY=unix"+os.environ['DISPLAY'],"-v=/tmp/.X11-unix:/tmp/.X11-unix:rw"] if p else []),
   ("graphics-card", lambda p: ["--device=/dev/dri/"+device for device in os.listdir("/dev/dri")] if p else []),
   ("serial-devices", lambda sd: ["--device=/dev/"+device for device in getSerialDevices()] if sd else []),
   ("system-dbus", lambda dbus: ["--volume=/var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket"] if dbus else []),
   ("as-root", lambda root: ["--user=0"] if root else ["--user="+str(os.getuid())]),
   # Anarchistic permissions
   ("privileged", lambda p: ["--privileged"] if p else [])])

def getCommand(subuserToRun, imageId, imageArgs):
  """
  Returns the command requred to run the subuser as a list of string arguments.
  Exits, printing an error message, if the subuser cannot be run due to no proper image for it being installed.
  """
  if not(subuserToRun.getImageId() and subuserToRun.getImageId() in subuserToRun.getUser().getInstalledImages() and subuserToRun.getUser().getInstalledImages()[subuserToRun.getImageId()].isDockerImageThere()):
    sys.exit("Image for "+subuserToRun.getName()+" is not installed. Try running:\n $subuser repair")

  flags = getBasicFlags()
  permissionFlagDict = getPermissionFlagDict(subuserToRun)
  permissions = subuserToRun.getPermissions()
  for permission, flagGenerator in permissionFlagDict.items():
    flags.extend(flagGenerator(permissions[permission]))

  return ["run"]+flags+[imageId]+[subuserToRun.getPermissions()["executable"]]+imageArgs

def getPrettyCommand(subuserToRun,imageId,imageArgs):
  """
  Get a command for pretty printing for use with dry-run.
  """
  command = getCommand(subuserToRun,imageId,imageArgs)
  return "docker '"+"' '".join(command)+"'"

def run(subuserToRun,imageArgs):
  if not subuserToRun.getPermissions()["executable"]:
    sys.exit("Cannot run subuser, no executable configured in permissions.json file.")
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

  imageId = buildRunReadyImageForSubuser(subuserToRun)
  #print(imageId)
  subuserToRun.getUser().getDockerDaemon().execute(getCommand(subuserToRun,imageId,imageArgs))
  try:
    subuserToRun.getUser().getDockerDaemon().removeImage(imageId)
  except subuserlib.classes.dockerDaemon.ImageDoesNotExistsException:
    pass

