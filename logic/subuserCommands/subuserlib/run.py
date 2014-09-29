#!/usr/bin/env python # This file should be compatible with both Python 2 and 3.
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

def generateImagePreparationDockerfile(subuserToRun):
  """
  There is still some preparation that needs to be done before an image is ready to be run.  But this preparation requires run time information, so we cannot preform that preparation at build time.
  """
  dockerfileContents  = "FROM "+subuserToRun.getImageId()+"\n"
  dockerfileContents += "RUN useradd --uid="+str(os.getuid())+" "+getpass.getuser()+" ;export exitstatus=$? ; if [ $exitstatus -eq 4 ] ; then echo uid exists ; elif [ $exitstatus -eq 9 ]; then echo username exists. ; else exit $exitstatus ; fi\n"
  if subuserToRun.getPermissions()["serial-devices"]:
    dockerfileContents += "RUN groupadd dialout; export exitstatus=$? ; if [ $exitstatus -eq 4 ] ; then echo gid exists ; elif [ $exitstatus -eq 9 ]; then echo groupname exists. ; else exit $exitstatus ; fi\n"
    dockerfileContents += "RUN groupadd uucp; export exitstatus=$? ; if [ $exitstatus -eq 4 ] ; then echo gid exists ; elif [ $exitstatus -eq 9 ]; then echo groupname exists. ; else exit $exitstatus ; fi\n"
    dockerfileContents += "RUN usermod -a -G dialout "+getpass.getuser()+"\n"
    dockerfileContents += "RUN usermod -a -G uucp "+getpass.getuser()+"\n"
  return dockerfileContents

def buildRunReadyImageForSubuser(subuserToRun):
  """
  Returns the Id of the Docker image to be run.
  """
  return subuserToRun.getUser().getDockerDaemon().build(None,quiet=True,useCache=True,rm=False,dockerfile=generateImagePreparationDockerfile(subuserToRun))

def getSerialDevices():
  return [device for device in os.listdir("/dev/") if device.startswith("ttyS") or device.startswith("ttyUSB") or device.startswith("ttyACM")]

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
   "allow-network-access" : lambda p: ["--net=bridge","--dns=8.8.8.8"] if p else ["--net=none"],
   "system-dirs" : lambda systemDirs: ["-v="+systemDir+":"+systemDir+":ro" for systemDir in systemDirs],
   "user-dirs" : lambda userDirs : ["-v="+os.path.join(subuserToRun.getUser().homeDir,userDir)+":"+os.path.join("/userdirs/",userDir)+":rw" for userDir in userDirs],
   "access-working-directory" : lambda p: ["-v="+os.getcwd()+":/pwd:rw","--workdir=/pwd"] if p else ["--workdir="+subuserToRun.getDockersideHome()],
   "stateful-home" : lambda p : ["-v="+subuserToRun.getHomeDirOnHost()+":"+subuserToRun.getDockersideHome()+":rw","-e","HOME="+subuserToRun.getDockersideHome()] if p else [],
   "x11" : lambda p: ["-e","DISPLAY=unix"+os.environ['DISPLAY'],"-v=/tmp/.X11-unix:/tmp/.X11-unix:rw"] if p else [],
   "graphics-card" : lambda p:["-v=/dev/dri:/dev/dri:rw"] + ["--device=/dev/dri/"+device for device in os.listdir("/dev/dri")] if p else [],
   "sound-card" : lambda p: ["-v=/dev/snd:/dev/snd:rw"]+["--device=/dev/snd/"+device for device in os.listdir("/dev/snd") if not device == "by-id" and not device == "by-path"] if p else [], #Why the volume here?  To make it so that the device nodes are owned by the audio group ;).  Evil, I know...
   "webcam" : lambda p: ["--volume=/dev/"+device+":/dev/"+device for device in os.listdir("/dev/") if device.startswith("video")] + ["--device=/dev/"+device for device in os.listdir("/dev/") if device.startswith("video")] if p else [],
   "serial-devices" : lambda sd: ["--volume=/dev/"+device+":/dev/"+device for device in getSerialDevices()] + ["--device=/dev/"+device for device in getSerialDevices()] if sd else [],
   "system-dbus" : lambda dbus: ["--volume=/var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket"] if dbus else [],
   "privileged" : lambda p: ["--privileged"] if p else [],
   "as-root" : lambda root: ["--user=0"] if root else ["--user="+str(os.getuid())]
   }

def getCommand(subuserToRun, imageId, imageArgs):
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

  return ["run"]+flags+[imageId]+[subuserToRun.getPermissions()["executable"]]+imageArgs

def getPrettyCommand(subuserToRun,imageId,imageArgs):
  """
  Get a command for pretty printing for use with dry-run.
  """
  command = getCommand(subuserToRun,imageId,imageArgs)
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

  imageId = buildRunReadyImageForSubuser(subuserToRun)
  #print(imageId)
  subuserToRun.getUser().getDockerDaemon().execute(getCommand(subuserToRun,imageId,imageArgs))
  try:
    subuserToRun.getUser().getDockerDaemon().removeImage(imageId)
  except subuserlib.classes.dockerDaemon.ImageDoesNotExistsException:
    pass

