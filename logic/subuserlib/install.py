#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
"""
Implements functions involved in building/installing/updating subuser images.
"""

#external imports
import sys,os,stat,uuid,io
#internal imports
import subuserlib.classes.installedImage, subuserlib.installedImages,subuserlib.classes.dockerDaemon,subuserlib.installTime,subuserlib.verify

def cleanUpAndExitOnError(user,error):
  user.getRegistry().log(str(error))
  user.getRegistry().log("Cleaning up.")
  sys.exit(1)

def installFromBaseImage(imageSource):
  """
  Build a docker base image using a script and return the image's Id.
  """
  buildImageScriptPath = os.path.join(imageSource.getSourceDir(),"docker-image", "BuildImage.sh")
  print("""\nATTENTION!

  Installing <"""+imageSource.getName()+"""> requires that the following shell script be run on your computer: <"""+buildImageScriptPath+"""> If you do not trust this shell script do not run it as it may be faulty or malicious!

  - Do you want to view the full contents of this shell script [v]?
  - Do you want to continue? (Type "run" to run the shell script)
  - To quit, press [q].

  [v/run/Q]: """)
  try:
    userInput = sys.stdin.readline().strip()
  except KeyboardInterrupt:
    cleanUpAndExitOnError(imageSource.getUser(),"\nOperation aborted.  Exiting.")

  if userInput == "v":
    print('\n===================== SCRIPT CODE =====================\n')
    with io.open(buildImageScriptPath, 'r',encoding="utf-8") as file_f:
      print(file_f.read())
    print('\n===================== END SCRIPT CODE =====================\n')
    return installFromBaseImage(imageSource)

  if userInput == "run":
    #Build the image using the script
    st = os.stat(buildImageScriptPath)
    os.chmod(buildImageScriptPath, stat.S_IMODE(st.st_mode) | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    imageTag = "subuser-"+str(uuid.uuid4())
    subuserlib.subprocessExtras.subprocessCheckedCall([buildImageScriptPath,imageTag])
    # Return the Id of the newly created image
    imageProperties = imageSource.getUser().getDockerDaemon().getImageProperties(imageTag)
    if imageProperties == None:
      cleanUpAndExitOnError(imageSource.getUser(),"Image failed to build.  The script exited successfully, but did not result in any Docker image being imported.")
    else:
      return imageProperties["Id"]
  cleanUpAndExitOnError(imageSource.getUser(),"Will not run install script.  Nothing to do.  Exiting.")

def installFromSubuserImagefile(imageSource, useCache=False,parent=None):
  """
  Returns the Id of the newly installed image.
  """
  dockerFileContents = imageSource.generateDockerfileConents(parent=parent)
  dockerImageDir = os.path.join(imageSource.getSourceDir(),"docker-image")
  imageId = imageSource.getUser().getDockerDaemon().build(directoryWithDockerfile=dockerImageDir,rm=True,useCache=useCache,dockerfile=dockerFileContents)
  return imageId

def installImage(imageSource, useCache=False,parent=None):
  """
  Install a image by building the given ImageSource.
  Register the newly installed image in the user's InstalledImages list.
  Return the Id of the newly installedImage.
  """
  imageSource.getUser().getRegistry().logChange("Installing "+imageSource.getName()+" ...")
  buildType = imageSource.getBuildType()
  if buildType == "SubuserImagefile":
    imageId = installFromSubuserImagefile(imageSource,useCache=useCache,parent=parent)
  elif buildType == "BuildImage.sh":
    imageId = installFromBaseImage(imageSource)
  else:
    cleanUpAndExitOnError(imageSource.getUser(),"No buildfile found: There needs to be a 'SubuserImagefile' or a 'BuildImage.sh' in the docker-image directory.")

  lastUpdateTime = imageSource.getPermissions()["last-update-time"]
  if lastUpdateTime == None:
    lastUpdateTime = subuserlib.installTime.currentTimeString()

  subuserSetupDockerFile = ""
  subuserSetupDockerFile += "FROM "+imageId+"\n"
  subuserSetupDockerFile += "RUN mkdir /subuser ; echo "+str(uuid.uuid4())+" > /subuser/uuid\n" # This ensures that all images have unique Ids.  Even images that are otherwise the same.
  imageId = imageSource.getUser().getDockerDaemon().build(dockerfile=subuserSetupDockerFile)
  
  imageSource.getUser().getInstalledImages()[imageId] = subuserlib.classes.installedImage.InstalledImage(imageSource.getUser(),imageId,imageSource.getName(),imageSource.getRepository().getName(),lastUpdateTime)
  imageSource.getUser().getInstalledImages().save()
  return imageId

def getImageSourceLineage(imageSource):
  """
  Return the lineage of the ProgrmSource, going from its base dependency up to itself.
  """
  try:
    dependency = imageSource.getDependency()
  except subuserlib.classes.imageSource.SyntaxError as syntaxError:
    cleanUpAndExitOnError(imageSource.getUser(),"Error while building image: "+ str(syntaxError))
  if dependency:
    return getImageSourceLineage(dependency) + [imageSource]
  else:
    return [imageSource]

def installLineage(imageSourceLineage,parent=None):
  """
  Install the lineage of image sources.
  Return the image id of the final installed image.
  """
  for imageSource in imageSourceLineage:
    parent = installImage(imageSource,parent=parent)
  return parent

def doImagesMatch(installedImage,imageSource):
  return installedImage.getImageSourceName() == imageSource.getName() and installedImage.getSourceRepoId() == imageSource.getRepository().getName()

def doLastUpdateTimesMatch(installedImage,imageSource):
  return installedImage.getLastUpdateTime() == imageSource.getPermissions()["last-update-time"] or not imageSource.getPermissions()["last-update-time"]

def compareSourceLineageAndInstalledImageLineage(user,sourceLineage,installedImageLineage):
  if not len(sourceLineage) == len(installedImageLineage):
    user.getRegistry().log("Number of dependencies changed from "+str(len(installedImageLineage))+" to "+str(len(sourceLineage)))
    print("Image sources:")
    for imageSource in sourceLineage:
      print(imageSource.getName())
    print("Installed images:")
    for installedImage in installedImageLineage:
      print(installedImage.getImageSourceName())
    return False

  lineage = zip(sourceLineage,installedImageLineage)
  for imageSource,installedImage in lineage:
    imagesMatch =  doImagesMatch(installedImage,imageSource)
    lastUpdateTimesMatch = doLastUpdateTimesMatch(installedImage,imageSource)
    if not (imagesMatch and lastUpdateTimesMatch):
      if not imagesMatch:
        user.getRegistry().log("Dependency changed for image from "+installedImage.getImageSourceName()+"@"+installedImage.getSourceRepoId()+" to "+imageSource.getName()+"@"+imageSource.getRepository().getName())
      elif not lastUpdateTimesMatch:
        user.getRegistry().log("Installed image "+installedImage.getImageSourceName()+"@"+installedImage.getSourceRepoId()+" is out of date.\nInstalled version:\n "+installedImage.getLastUpdateTime()+"\nCurrent version:\n "+str(imageSource.getPermissions()["last-update-time"])+"\n")
      return False
  return True

def isInstalledImageUpToDate(installedImage):
  """
  Returns True if the installed image(including all of its dependencies, is up to date.  False otherwise.
  """
  try:
    topImageSource = installedImage.getUser().getRegistry().getRepositories()[installedImage.getSourceRepoId()][installedImage.getImageSourceName()]
  except KeyError: # Image source not found, therefore updating would be pointless.
    return True

  sourceLineage = getImageSourceLineage(topImageSource)
  installedImageLineage = subuserlib.installedImages.getImageLineage(installedImage.getUser(),installedImage.getImageId())
  return compareSourceLineageAndInstalledImageLineage(installedImage.getUser(),sourceLineage,installedImageLineage)

def ensureSubuserImageIsInstalledAndUpToDate(subuser, useCache=False):
  """
  Ensure that the Docker image associated with the subuser is installed and up to date.
  If the image is already installed, but is out of date, or it's dependencies are out of date, build it again.
  Otherwise, do nothing.
  """
  # get dependency list as a list of ImageSources
  sourceLineage = getImageSourceLineage(subuser.getImageSource())
  parentId=None
  while len(sourceLineage) > 0:
    imageSource = sourceLineage.pop(0)
    latestInstalledImage = imageSource.getLatestInstalledImage()
    if not latestInstalledImage or not isInstalledImageUpToDate(latestInstalledImage):
      subuser.setImageId(installLineage([imageSource]+sourceLineage,parent=parentId))
      subuser.getUser().getRegistry().logChange("Installed new image for subuser "+subuser.getName())
      return
    parentId=latestInstalledImage.getImageId()
  if not subuser.getImageId() == parentId:
    subuser.setImageId(parentId)
    subuser.getUser().getRegistry().logChange("Installed new image for subuser "+subuser.getName())

