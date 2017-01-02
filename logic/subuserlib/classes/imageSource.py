# -*- coding: utf-8 -*-

"""
Images in subuser are built from ImageSource objects.
"""

#external imports
import os
import uuid
#internal imports
from subuserlib.classes.userOwnedObject import UserOwnedObject
from subuserlib.classes.describable import Describable
import subuserlib.permissions
import subuserlib.docker
import subuserlib.classes.docker.dockerDaemon as dockerDaemon
import subuserlib.classes.exceptions as exceptions
import subuserlib.print

class ImageSource(UserOwnedObject,Describable):
  def __init__(self,user,repo,name,explicitConfig=None):
    self.__name = name
    self.__repo = repo
    self.__permissions = None
    self.__explicitConfig = explicitConfig
    UserOwnedObject.__init__(self,user)

  def __hash__(self):
    return hash(self.getIdentifier())

  def getName(self):
    return self.__name

  def getIdentifier(self):
    """
    Return a standard human readable identifier for an ImageSource.
    """
    return self.getName() + "@" + self.getRepository().getDisplayName()

  def getDockerImageTag(self):
    longTag = "subuser-" + self.getUser().getEndUser().name + "-" + self.getIdentifier()
    return subuserlib.docker.buildImageTag(longTag,self.getHash())

  def getRepository(self):
    """
    Get the repository where this ImageSource resides.
    """
    return self.__repo

  def getSubusers(self):
    """
     Get a list of subusers that were built from this ImageSource.
    """
    subusers = []
    for subuser in self.getUser().getRegistry().getSubusers():
      if subuser.getImageSource()==self:
        subusers.append(subuser)
    return subusers

  def getImageDir(self):
    if self.__explicitConfig:
      return self.__explicitConfig["build-context"]
    imageDir = os.path.join(self.getRelativeSourceDir(),"image")
    # If the image dir does not exist,
    # Look for the old, deprecated, docker-image dir
    if not self.getRepository().getFileStructure().exists(imageDir):
      imageDir = os.path.join(self.getRelativeSourceDir(),"docker-image")
      if not self.getRepository().getFileStructure().exists(imageDir):
        raise exceptions.ImageBuildException("Image source "+self.getIdentifier()+ " does not have an image dir with sources from which to build.")
    return imageDir

  def getSourceDir(self):
    return os.path.join(self.getRepository().getImageSourcesDir(),self.getName())

  def getRelativeSourceDir(self):
    return os.path.join(self.getRepository().getRelativeImageSourcesDir(),self.getName())

  def getLatestInstalledImage(self):
    """
    Get the most up-to-date InstalledImage based on this ImageSource.
    Returns None if no images have been installed from this ImageSource.
    """
    imageCreationDateTimeBestSoFar=''
    mostUpToDateImage = None
    for installedImage in self.getInstalledImages():
      thisImagesCreationDateTime = installedImage.getCreationDateTime()
      if thisImagesCreationDateTime > imageCreationDateTimeBestSoFar:
        mostUpToDateImage = installedImage
        imageCreationDateTimeBestSoFar = thisImagesCreationDateTime
    return mostUpToDateImage

  def getInstalledImages(self):
    """
    Return the installed images which are based on this image.
    """
    installedImagesBasedOnThisImageSource = []
    for _,installedImage in self.getUser().getInstalledImages().items():
      if installedImage.getImageSourceName() == self.getName() and installedImage.getSourceRepoId() == self.getRepository().getName():
        installedImagesBasedOnThisImageSource.append(installedImage)
    return installedImagesBasedOnThisImageSource

  def getPermissionsFilePath(self):
    relativePath = self.getRelativePermissionsFilePath()
    return os.path.join(self.getRepository().getRepoPath(),relativePath)

  def getRelativePermissionsFilePath(self):
    if self.__explicitConfig is not None:
      return self.__explicitConfig["permissions-file"]
    if "dependent" in self.getRelativeSourceDir():
      raise Exception(str(self.__explicitConfig)+"\n"+self.getName()+str(self.getRepository().keys()))
    return os.path.join(self.getRelativeSourceDir(),"permissions.json")

  def getPermissions(self):
    if not self.__permissions:
      permissionsString = self.getRepository().getFileStructure().read(self.getRelativePermissionsFilePath())
      initialPermissions = subuserlib.permissions.load(permissionsString=permissionsString)
      self.__permissions = subuserlib.classes.permissions.Permissions(self.getUser(),initialPermissions,writePath=self.getPermissionsFilePath())
    return self.__permissions

  def describe(self):
    """
    Describe this ImageSource including it's default permissions.

    Prints to standard output.
    """
    subuserlib.print.printWithoutCrashing(self.getIdentifier())
    self.getPermissions().describe()

  def build(self,parent,useCache=False):
    imageFileType = self.getImageFileType()
    if imageFileType == "Dockerfile":
      dockerfileContents = self.getImageFileContents()
    elif imageFileType == "SubuserImagefile":
      subuserImagefileContents = self.getImageFileContents()
      dockerfileContents = ""
      for line in subuserImagefileContents.split("\n"):
        if line.startswith("FROM-SUBUSER-IMAGE"):
          dockerfileContents = "FROM " + parent + "\n"
        else:
          dockerfileContents += line + "\n"
    imageId = self.getUser().getDockerDaemon().build(relativeBuildContextPath=self.getImageDir(),repositoryFileStructure=self.getRepository().getFileStructure(),rm=True,dockerfile=dockerfileContents,useCache=useCache)
    subuserSetupDockerFile = ""
    subuserSetupDockerFile += "FROM "+imageId+"\n"
    subuserSetupDockerFile += "RUN mkdir -p /subuser ; echo "+str(uuid.uuid4())+" > /subuser/uuid\n" # This ensures that all images have unique Ids.  Even images that are otherwise the same.
    return self.getUser().getDockerDaemon().build(dockerfile=subuserSetupDockerFile,tag=self.getDockerImageTag(),useCache=False)

  def getImageFile(self):
    if self.__explicitConfig:
      return self.__explicitConfig["image-file"]
    dockerfilePath = os.path.join(self.getImageDir(),"Dockerfile")
    if self.getRepository().getFileStructure().exists(dockerfilePath):
      return dockerfilePath
    subuserImagefilePath = os.path.join(self.getImageDir(),"SubuserImagefile")
    if self.getRepository().getFileStructure().exists(subuserImagefilePath):
      return subuserImagefilePath

  def getImageFileType(self):
    return os.path.basename(self.getImageFile())

  def getImageFileContents(self):
    return self.getRepository().getFileStructure().read(self.getImageFile())

  def getDependency(self):
    """
     Returns the dependency of this ImageSource as a ImageSource.
     Or None if there is no dependency.
    """
    if not self.getImageFileType() == "SubuserImagefile":
      return None
    subuserImagefileContents = self.getImageFileContents()
    lineNumber=0
    for line in subuserImagefileContents.split("\n"):
      if line.startswith("FROM-SUBUSER-IMAGE"):
        try:
          import subuserlib.resolve
          imageURI = line.split(" ")[1]
          return subuserlib.resolve.resolveImageSource(self.getUser(),imageURI,contextRepository=self.getRepository(),allowLocalRepositories=False) #TODO, ImageSource names with spaces or other funny characters...
        except IndexError:
          raise exceptions.ImageBuildException("Syntax error in SubuserImagefile one line "+str(lineNumber)+":\n"+line)
        except KeyError:
          raise exceptions.ImageBuildException("Error in "+self.getName()+"'s SubuserImagefile on line "+str(lineNumber)+"\n Subuser image does not exist: \""+imageURI+"\"")
      lineNumber+=1
    return None

  def getHash(self):
    """ Return the hash of the ``image`` directory. """
    return self.getRepository().getFileStructure().hash(self.getImageDir())
