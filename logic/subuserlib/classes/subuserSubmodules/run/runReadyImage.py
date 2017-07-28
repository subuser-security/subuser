# -*- coding: utf-8 -*-

"""
Contains code that prepairs a subuser's image to be run.
"""

#external imports
import os
import hashlib
#internal imports
from subuserlib.classes.userOwnedObject import UserOwnedObject
import subuserlib.classes.exceptions
import subuserlib.docker

class RunReadyImage(UserOwnedObject):
  """
  This class represents the run ready image associated with a given subuser. It is tied to the subuser and its latest permissions.
  """
  def __init__(self,user,subuser):
    self.subuser = subuser
    self.__id = None
    UserOwnedObject.__init__(self,user)

  def setup(self):
    if not "run-ready-image-id" in self.subuser.getRuntimeCache():
      if not self.subuser.isImageInstalled():
        self.user.registry.log("No working image for subuser "+self.subuser.name+" unable to prepair run ready image.")
        return
      self.__id = self.build()
      self.subuser.getRuntimeCache()["run-ready-image-id"] = self.__id
      self.subuser.getRuntimeCache().save()

  @property
  def id(self):
    if not self.__id:
      self.__id = self.subuser.getRuntimeCache()["run-ready-image-id"]
    return self.__id

  @property
  def sourceHash(self):
    """
    Return the SHA512 hash of the Dockerfile used to generate the latest RunReadyImage
    """
    hasher = hashlib.sha512()
    hasher.update(self.generateImagePreparationDockerfile().encode("utf-8"))
    return hasher.hexdigest()

  def generateImagePreparationDockerfile(self):
    """
    There is still some preparation that needs to be done before an image is ready to be run.  But this preparation requires run time information, so we cannot preform that preparation at build time.
    """
    dockerfileContents  = "FROM "+self.subuser.imageId+"\n"
    dockerfileContents += "RUN useradd --uid="+str(self.user.endUser.uid)+" subuser ;export exitstatus=$? ; if [ $exitstatus -eq 4 ] ; then echo uid exists ; elif [ $exitstatus -eq 9 ]; then echo username exists. ; else exit $exitstatus ; fi\n"
    dockerfileContents += "RUN test -d /home/subuser || mkdir /home/subuser && chown subuser /home/subuser\n"
    if self.subuser.permissions["serial-devices"]:
      dockerfileContents += "RUN groupadd dialout; export exitstatus=$? ; if [ $exitstatus -eq 4 ] ; then echo gid exists ; elif [ $exitstatus -eq 9 ]; then echo groupname exists. ; else exit $exitstatus ; fi\n"
      dockerfileContents += "RUN groupadd uucp; export exitstatus=$? ; if [ $exitstatus -eq 4 ] ; then echo gid exists ; elif [ $exitstatus -eq 9 ]; then echo groupname exists. ; else exit $exitstatus ; fi\n"
      dockerfileContents += "RUN usermod -a -G dialout "+self.user.endUser.name+"\n"
      dockerfileContents += "RUN usermod -a -G uucp "+self.user.endUser.name+"\n"
    if self.subuser.permissions["sudo"]:
      dockerfileContents += "RUN (umask 337; echo \""+self.user.endUser.name+" ALL=(ALL) NOPASSWD: ALL\" > /etc/sudoers.d/allowsudo )\n"
    return dockerfileContents

  def build(self):
    """
    Returns the Id of the Docker image to be run.
    """
    try:
      tag = subuserlib.docker.buildImageTag("subuser-"+self.user.endUser.name+"-"+self.subuser.name,self.subuser.permissions.getHash())
      return self.user.dockerDaemon.build(None,quietClient=True,useCache=True,tag=tag,forceRm=True,rm=True,dockerfile=self.generateImagePreparationDockerfile())
    except subuserlib.classes.exceptions.ImageBuildException as e:
      self.user.registry.log("Error building run-ready image for subuser "+self.subuser.name+"\n"+str(e))
      return None
