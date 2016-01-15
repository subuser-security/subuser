# -*- coding: utf-8 -*-

"""
Container objects allow you to interact with docker containers via the Docker daemon.
"""

#external imports
import json,urllib
#internal imports
from subuserlib.classes.userOwnedObject import UserOwnedObject

class Container(UserOwnedObject):
  def __init__(self,user,containerId):
    self.__containerId = containerId
    UserOwnedObject.__init__(self,user)

  def inspect(self):
    """
     Returns a dictionary of container properties.
     If the container no longer exists, return None.
    """
    self.getUser().getDockerDaemon().getConnection().request("GET","/v1.13/containers/"+self.__containerId+"/json")
    response = self.getUser().getDockerDaemon().getConnection().getresponse()
    if not response.status == 200:
      response.read() # Read the response and discard it to prevent the server from getting locked up: http://stackoverflow.com/questions/3231543/python-httplib-responsenotready
      return None
    else:
      return json.loads(response.read().decode("utf-8"))

  def stop(self):
    self.getUser().getDockerDaemon().getConnection().request("POST","/v1.13/containers/"+self.getId()+"/stop")
    response = self.getUser().getDockerDaemon().getConnection().getresponse()
    response.read()

  def remove(self,force=False):
    queryParameters =  {
      'force': force
      }
    try:
      queryParametersString = urllib.urlencode(queryParameters)
    except AttributeError:
      queryParametersString = urllib.parse.urlencode(queryParameters) # Python 3
    self.getUser().getDockerDaemon().getConnection().request("DELETE","/v1.13/containers/"+self.getId()+"?"+queryParametersString)
    response = self.getUser().getDockerDaemon().getConnection().getresponse()
    response.read()

  def getId(self):
    return self.__containerId
