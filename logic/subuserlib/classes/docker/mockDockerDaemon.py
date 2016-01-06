# -*- coding: utf-8 -*-
# pylint: disable=unused-argument

"""
In order to make our test suit work, we must use a MockDockerDaemon rather than communicating with a real Docker instance.
"""

#external imports
import json
import os
#internal imports
from subuserlib.classes.userOwnedObject import UserOwnedObject
import subuserlib.classes.docker.dockerDaemon
import subuserlib.print

class MockDockerDaemon(UserOwnedObject):
  def __init__(self,user):
    self.images = {}
    self.nextImageId = 1
    self.newId = None
    UserOwnedObject.__init__(self,user)
    self.imagesPath = os.path.join(user.homeDir,"docker/images.json")
    self.__load()
    self.dockerDaemon = subuserlib.classes.docker.dockerDaemon.RealDockerDaemon(user)
    self.connection = MockConnection(self)
    self.dockerDaemon.getConnection = self.getConnection
    self.dockerDaemon.getImageProperties = self.getImageProperties

  def __load(self):
    with open(self.imagesPath,"r") as imagesFile:
      self.images = json.load(imagesFile)

  def __save(self):
    with open(self.imagesPath,"w") as imagesFile:
      json.dump(self.images,imagesFile)

  def getConnection(self):
    return self.connection

  def getImageProperties(self,imageTagOrId):
    """
     Returns a dictionary of image properties, or None if the image does not exist.
    """
    if imageTagOrId in self.images:
      return self.images[imageTagOrId]
    else:
      return None

  def build(self,relativeBuildContextPath=None,repositoryFileStructure=None,useCache=True,rm=True,forceRm=True,quiet=False,quietClient=False,tag=None,dockerfile=None):
    """
    Build a Docker image.  If a the dockerfile argument is set to a string, use that string as the Dockerfile.  Return the newly created images Id or raises an exception if the build fails.
    """
    while str(self.nextImageId) in self.images:
      self.nextImageId = self.nextImageId+1
    self.newId = str(self.nextImageId)
    parent = dockerfile.split("\n")[0].split(" ")[1].rstrip()
    if "debian" in dockerfile:
      parent = ""
    self.images[self.newId] = {"Id":self.newId,"Parent":parent,"Created":str(len(self.images))}
    self.__save()
    self.dockerDaemon.build(relativeBuildContextPath=relativeBuildContextPath,repositoryFileStructure=repositoryFileStructure,useCache=useCache,rm=rm,forceRm=forceRm,quiet=quiet,tag=tag,dockerfile=dockerfile,quietClient=quietClient)
    return self.newId

  def removeImage(self,imageId):
    del self.images[imageId]
    self.__save()

  def getInfo(self):
    return {"Foo":"bar"}

  def execute(self,args,cwd=None,background=False,backgroundSuppressOutput=True,backgroundCollectStdout=False,backgroundCollectStderr=False):
    subuserlib.print.printWithoutCrashing("Execute docker with args: "+str(args))
    subuserlib.print.printWithoutCrashing("Cwd:"+str(cwd))

class MockResponse():
  def __init__(self,mockDockerDaemon):
    self.mockDockerDaemon = mockDockerDaemon
    self.status = 200
    self.body = b"{\"stream\":\"Building"+"→→→".encode("utf-8")+b"\"}\n{\"stream\":\"Building...\"}\n{\"stream\":\"Building...\"}\n{\"stream\":\"Successfully built "+mockDockerDaemon.newId.encode("utf-8")+b"\"}"

  def read(self,bytes=None):
    if bytes:
      value = self.body[:bytes]
      self.body = self.body[bytes:]
      return value
    else:
      return self.body

class MockConnection():
  def __init__(self,mockDockerDaemon):
    self.mockDockerDaemon = mockDockerDaemon
    self.newId = None

  def request(self,method,url,body=None,headers=None):
    pass

  def getresponse(self):
    return MockResponse(self.mockDockerDaemon)
