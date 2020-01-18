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
    self.id = containerId
    UserOwnedObject.__init__(self,user)

  def inspect(self):
    """
     Returns a dictionary of container properties.
     If the container no longer exists, return None.
    """
    self.user.dockerDaemon.getConnection().request("GET","/v1.13/containers/"+self.id+"/json")
    response = self.user.dockerDaemon.getConnection().getresponse()
    if not response.status == 200:
      response.read() # Read the response and discard it to prevent the server from getting locked up: https://stackoverflow.com/questions/3231543/python-httplib-responsenotready
      return None
    else:
      return json.loads(response.read().decode("utf-8"))

  def stop(self):
    self.user.dockerDaemon.getConnection().request("POST","/v1.13/containers/"+self.id+"/stop")
    response = self.user.dockerDaemon.getConnection().getresponse()
    response.read()

  def remove(self,force=False):
    queryParameters =  {
      'force': force
      }
    try:
      queryParametersString = urllib.urlencode(queryParameters)
    except AttributeError:
      queryParametersString = urllib.parse.urlencode(queryParameters) # Python 3
    self.user.dockerDaemon.getConnection().request("DELETE","/v1.13/containers/"+self.id+"?"+queryParametersString)
    response = self.user.dockerDaemon.getConnection().getresponse()
    response.read()

