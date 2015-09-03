#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

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
import subuserlib.classes.docker.dockerDaemon as dockerDaemon

class ImageSource(UserOwnedObject,Describable):
  def __init__(self,user,repo,name):
    self.__name = name
    self.__repo = repo
    self.__permissions = None
    UserOwnedObject.__init__(self,user)

  def getName(self):
    return self.__name

  def getIdentifier(self):
    """
    Return a standard human readable identifier for an ImageSource.
    """
    return self.getName() + "@" + self.getRepository().getDisplayName()

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

  def getDockerImageDir(self):
    repoConfig = self.getRepository().getRepoConfig()
    if repoConfig and "docker-image-dir" in repoConfig:
      return os.path.join(self.getRelativeSourceDir(),repoConfig["docker-image-dir"])
    else:
      return os.path.join(self.getRelativeSourceDir(),"docker-image")

  def getSourceDir(self):
    return os.path.join(self.getRepository().getSubuserRepositoryRoot(),self.getName())

  def getRelativeSourceDir(self):
    return os.path.join(self.getRepository().getSubuserRepositoryRelativeRoot(),self.getName())

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
    return os.path.join(self.getSourceDir(),"permissions.json")

  def getPermissions(self):
    if not self.__permissions:
      permissionsString = self.getRepository().getFileStructure().read(os.path.join(self.getRepository().getSubuserRepositoryRelativeRoot(),self.getName(),"permissions.json"))
      initialPermissions = subuserlib.permissions.load(permissionsString=permissionsString)
      self.__permissions = subuserlib.classes.permissions.Permissions(self.getUser(),initialPermissions,writePath=self.getPermissionsFilePath())
    return self.__permissions

  def describe(self):
    """
    Describe this ImageSource including it's default permissions.

    Prints to standard output.
    """
    print(self.getIdentifier())
    self.getPermissions().describe()

  def build(self,parent):
    dockerFileContents = self.getDockerfileContents(parent=parent)
    imageId = self.getUser().getDockerDaemon().build(relativeBuildContextPath=self.getDockerImageDir(),repositoryFileStructure=self.getRepository().getFileStructure(),rm=True,dockerfile=dockerFileContents)
    subuserSetupDockerFile = ""
    subuserSetupDockerFile += "FROM "+imageId+"\n"
    subuserSetupDockerFile += "RUN mkdir /subuser ; echo "+str(uuid.uuid4())+" > /subuser/uuid\n" # This ensures that all images have unique Ids.  Even images that are otherwise the same.
    return self.getUser().getDockerDaemon().build(dockerfile=subuserSetupDockerFile)

  def getRelativeSubuserImagefilePath(self):
    """
    Returns the relative path to the SubuserImagefile, whether it exists or not.
    """
    dockerImageDir = self.getDockerImageDir()
    return os.path.join(dockerImageDir,"SubuserImagefile")

  def getSubuserImagefileContents(self):
    """
     Returns the contents of the SubuserImagefile.  If there is no SubuserImagefile return None.
    """
    try:
      return self.getRepository().getFileStructure().read(self.getRelativeSubuserImagefilePath())
    except (OSError,IOError):
      return None

  def getDockerfileContents(self,parent=None):
    """
    Returns a string representing the Dockerfile that is to be used to build this ImageSource.
    """
    dockerImageDir = self.getDockerImageDir()
    dockerfilePath = os.path.join(dockerImageDir,"Dockerfile")
    try:
      return self.getRepository().getFileStructure().read(dockerfilePath)
    except (OSError,IOError):
      pass
    subuserImagefileContents = self.getSubuserImagefileContents()
    if subuserImagefileContents is None:
      raise dockerDaemon.ImageBuildException("No build file found for image:" + self.getIdentifier()+"\nEvery image must have a valid Dockerfile or SubuserImageFile")
    dockerfileContents = ""
    for line in subuserImagefileContents.split("\n"):
      if line.startswith("FROM-SUBUSER-IMAGE"):
        dockerfileContents = dockerfileContents + "FROM "+parent+"\n"
      else:
        dockerfileContents = dockerfileContents +line+"\n"
    return dockerfileContents

  def getDependency(self):
    """
     Returns the dependency of this ImageSource as a ImageSource.
     Or None if there is no dependency.
    """
    subuserImagefileContents = self.getSubuserImagefileContents()
    if subuserImagefileContents == None:
      return None
    lineNumber=0
    for line in subuserImagefileContents.split("\n"):
      if line.startswith("FROM-SUBUSER-IMAGE"):
        try:
          import subuserlib.resolve
          imageURI = line.split(" ")[1]
          return subuserlib.resolve.resolveImageSource(self.getUser(),imageURI,contextRepository=self.getRepository(),allowRefferingToRepositoriesByName=False) #TODO, ImageSource names with spaces or other funny characters...
        except IndexError:
          raise SyntaxError("Syntax error in SubuserImagefile one line "+str(lineNumber)+":\n"+line)
        except KeyError:
          raise SyntaxError("Error in "+self.getName()+"'s SubuserImagefile on line "+str(lineNumber)+"\n Subuser image does not exist: \""+imageURI+"\"")
      lineNumber+=1
    return None

  def getHash(self):
    """ Return the hash of the ``docker-image`` directory. """
    return self.getRepository().getFileStructure().hash(self.getDockerImageDir())
