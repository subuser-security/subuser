# -*- coding: utf-8 -*-

"""
Contains code that prepairs a subuser's image to be run.
"""

#external imports
import os
#internal imports
from subuserlib.classes.userOwnedObject import UserOwnedObject
import subuserlib.classes.exceptions
import subuserlib.docker

class RunReadyImage(UserOwnedObject):
  def __init__(self,user,subuser):
    self.subuser = subuser
    self.__id = None
    UserOwnedObject.__init__(self,user)

  def setup(self):
    if not "run-ready-image-id" in self.subuser.getRuntimeCache():
      self.__id = self.build()
      self.subuser.getRuntimeCache()["run-ready-image-id"] = self.__id
      self.subuser.getRuntimeCache().save()

  @property
  def id(self):
    if not self.__id:
      self.__id = self.subuser.getRuntimeCache()["run-ready-image-id"]
    return self.__id

  def generateImagePreparationDockerfile(self):
    """
    There is still some preparation that needs to be done before an image is ready to be run.  But this preparation requires run time information, so we cannot preform that preparation at build time.
    """
    dockerfileContents  = "FROM "+self.subuser.imageId+"\n"
    dockerfileContents += "RUN useradd --uid="+str(self.user.endUser.uid)+" "+self.user.endUser.name+" ;export exitstatus=$? ; if [ $exitstatus -eq 4 ] ; then echo uid exists ; elif [ $exitstatus -eq 9 ]; then echo username exists. ; else exit $exitstatus ; fi\n"
    dockerfileContents += "RUN test -d "+self.user.endUser.homeDir+" || mkdir "+self.user.endUser.homeDir+" && chown "+self.user.endUser.name+" "+self.user.endUser.homeDir+"\n"
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
