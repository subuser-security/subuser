#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
Images in subuser are built from ImageSource objects.
"""

#external imports
import os,io
#internal imports
import subuserlib.classes.userOwnedObject,subuserlib.classes.describable,subuserlib.subprocessExtras,subuserlib.resolve, subuserlib.hashDirectory

class ImageSource(subuserlib.classes.userOwnedObject.UserOwnedObject,subuserlib.classes.describable.Describable):

  def __init__(self,user,repo,name):
    self.__name = name
    self.__repo = repo
    self.__permissions = None
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)

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

  def getSourceDir(self):
    return os.path.join(self.getRepository().getSubuserRepositoryRoot(),self.getName())

  def getBuildType(self):
    """
     Return the build type for this image source.  Or None, if no valid build files are found.  Possible build types are:
       - 'SubuserImagefile'
       - 'BuildImage.sh'
    """
    dockerImageDir = os.path.join(self.getSourceDir(),"docker-image")
    pathToBuildTypeMap = {
      "SubuserImagefile" : os.path.join(dockerImageDir,"SubuserImagefile"),
      "BuildImage.sh" : os.path.join(dockerImageDir,"BuildImage.sh")}
    myBuildType = None
    for buildType,path in pathToBuildTypeMap.items():
      if os.path.isfile(path):
        myBuildType = buildType
    return myBuildType

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

  def getPermissions(self):
    if not self.__permissions:
      permissionsPath=os.path.join(self.getSourceDir(),"permissions.json")
      self.__permissions = subuserlib.classes.permissions.Permissions(self.getUser(),readPath=permissionsPath,writePath=permissionsPath)
    return self.__permissions

  def describe(self):
    """
    Describe this ImageSource including it's default permissions.

    Prints to standard output.
    """
    print(self.getName()+":")
    self.getPermissions().describe()

  def getSubuserImagefilePath(self):
    """
    Returns the path to the SubuserImagefile, whether it exists or not.
    """
    dockerImageDir = os.path.join(self.getSourceDir(),"docker-image")
    return os.path.join(dockerImageDir,"SubuserImagefile")

  def getSubuserImagefileContents(self):
    """
     Returns the contents of the SubuserImagefile.  If there is no SubuserImagefile, raises an exception.
    """
    if os.path.isfile(self.getSubuserImagefilePath()):
      with io.open(self.getSubuserImagefilePath(),mode="r",encoding="utf-8") as subuserImagefile:
        return subuserImagefile.read()
    else:
      raise subuserlib.classes.dockerDaemon.ImageBuildException("This ImageSource does not build from a SubuserImagefile.")

  def generateDockerfileConents(self,parent=None):
    """
    Returns a string representing the Dockerfile that is to be used to build this ImageSource.
    """
    subuserImagefileContents = self.getSubuserImagefileContents()
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
    SubuserImagefileContents = self.getSubuserImagefileContents()
    lineNumber=0
    for line in SubuserImagefileContents.split("\n"):
      if line.startswith("FROM-SUBUSER-IMAGE"):
        try:
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
    return subuserlib.hashDirectory.getHashOfDirs(os.path.join(self.getSourceDir(),"docker-image"))

class SyntaxError(Exception):
  """
  A syntax error may be raised when parsing an ImageSource's ``Dockerfile``
  """
  pass

