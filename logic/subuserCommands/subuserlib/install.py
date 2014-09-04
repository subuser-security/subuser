#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import sys,os,stat,uuid,json
#internal imports
import subuserlib.classes.installedImage, subuserlib.installedImages,subuserlib.classes.dockerDaemon

def installFromBaseImage(programSource):
  """
  Build a docker base image using a script and return the image's Id.
  """
  buildImageScriptPath = os.path.join(programSource.getSourceDir(),"docker-image", "BuildImage.sh")
  print("""\nATTENTION!

  Installing <"""+programSource.getName()+"""> requires that the following shell script be run on your computer: <"""+buildImageScriptPath+"""> If you do not trust this shell script do not run it as it may be faulty or malicious!

  - Do you want to view the full contents of this shell script [v]?
  - Do you want to continue? (Type "run" to run the shell script)
  - To quit, press [q].

  [v/run/Q]: """)
  try:
    userInput = sys.stdin.readline().strip()
  except KeyboardInterrupt:
    sys.exit("\nOperation aborted.  Exiting.")

  if userInput == "v":
    print('\n===================== SCRIPT CODE =====================\n')
    with open(buildImageScriptPath, 'r') as file_f:
      print(file_f.read())
    print('\n===================== END SCRIPT CODE =====================\n')
    return installFromBaseImage(programSource)
  
  if userInput == "run":
    #Build the image using the script
    st = os.stat(buildImageScriptPath)
    os.chmod(buildImageScriptPath, stat.S_IMODE(st.st_mode) | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    imageTag = "subuser-"+str(uuid.uuid4())
    subprocessExtras.subprocessCheckedCall([buildImageScriptPath,imageTag])
    # Return the Id of the newly created image
    imageProperties = programSource.getUser().getDockerDaemon().getImageProperties(imageTag)
    if imageProperites == None:
      sys.exit("Image failed to build.  The script exited successfully, but did not result in any Docker image being imported.")
    else:
      return imageProperties["Id"]
  sys.exit("Will not run install script.  Nothing to do.  Exiting.")

def installFromSubuserImagefile(programSource, useCache=False,parent=None):
  """
  Returns the Id of the newly installed image.
  """
  dockerFileContents = programSource.generateDockerfileConents(parent=parent)
  try:
    dockerImageDir = os.path.join(programSource.getSourceDir(),"docker-image")
    id = programSource.getUser().getDockerDaemon().build(directoryWithDockerfile=dockerImageDir,rm=True,useCache=useCache,dockerfile=dockerFileContents)
    return id
  except subuserlib.classes.dockerDaemon.ImageBuildException as e:
    sys.exit("Installing image failed: "+programSource.getName()+"\n"+str(e))

def installProgram(programSource, useCache=False,parent=None):
  """
  Install a program by building the given ProgramSource.
  Register the newly installed image in the user's InstalledImages list.
  Return the Id of the newly installedImage.
  """
  print("Installing "+programSource.getName()+" ...")
  buildType = programSource.getBuildType()
  if buildType == "SubuserImagefile":
    imageId = installFromSubuserImagefile(programSource,useCache=useCache,parent=parent)
  elif buildType == "BuildImage.sh":
    imageId = installFromBaseImage(programSource)
  else:
    sys.exit("No buildfile found: There needs to be a 'SubuserImagefile' or a 'BuildImage.sh' in the docker-image directory.")

  lastUpdateTime = programSource.getPermissions()["last-update-time"]
  if lastUpdateTime == None:
    lastUpdateTime = installTime.currentTimeString()

  programSource.getUser().getInstalledImages()[imageId] = subuserlib.classes.installedImage.InstalledImage(programSource.getUser(),imageId,programSource.getName(),programSource.getRepository().getName(),lastUpdateTime)
  return imageId

def getProgramSourceLineage(programSource):
  """
  Return the lineage of the ProgrmSource, going from its base dependency up to itself.
  """
  dependency = programSource.getDependency()
  if dependency:
    return getProgramSourceLineage(dependency) + [programSource]
  else:
    return [programSource]

def installLineage(programSourceLineage,parent=None):
  """
  Install the lineage of program sources.
  Return the image id of the final installed image.
  """
  for programSource in programSourceLineage:
    parent = installProgram(programSource,parent=parent)
  return parent

def isInstalledImageUpToDate(installedImage):
  """
  Returns True if the installed image(including all of its dependencies, is up to date.  False otherwise.
  """
  installedImageSource = installedImage.getUser().getRegistry().getRepositories()[installedImage.getSourceRepoId()][installedImage.getProgramSourceName()]
  sourceLineage = getProgramSourceLineage(installedImageSource)
  installedImageLineage = subuserlib.installedImages.getImageLineage(installedImage.getUser(),installedImage.getImageId())
  while len(sourceLineage) > 0:
    if not len(installedImageLineage)>0:
      return False
    programSource = sourceLineage.pop(0)
    installedImage = installedImageLineage.pop(0)
    if not (installedImage.getProgramSourceName() == programSource.getName() and installedImage.getSourceRepoId() == programSource.getRepository().getName() and installedImage.getLastUpdateTime() == programSource.getPermissions()["last-update-time"]):
      return False
  return True
  
def ensureSubuserImageIsInstalledAndUpToDate(subuser, useCache=False):
  """
  Ensure that the Docker image associated with the subuser is installed and up to date.
  If the image is already installed, but is out of date, or it's dependencies are out of date, build it again.
  Otherwise, do nothing.
  """
  # get dependency list as a list of ProgramSources
  sourceLineage = getProgramSourceLineage(subuser.getProgramSource())
  parentId=None
  while len(sourceLineage) > 0:
    programSource = sourceLineage.pop(0)
    latestInstalledImage = programSource.getLatestInstalledImage()
    if not latestInstalledImage or not isInstalledImageUpToDate(latestInstalledImage):
      subuser.setImageId(installLineage([programSource]+sourceLineage,parent=parentId))
      subuser.getUser().getRegistry().logChange("Installed new image for subuser "+subuser.getName())
      return
    parentId=latestInstalledImage.getImageId()
  if not subuser.getImageId() == parentId:
    subuser.setImageId(parentId)
    subuser.getUser().getRegistry().logChange("Installed new image for subuser "+subuser.getName())

