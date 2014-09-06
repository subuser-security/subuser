#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import getpass, os, sys
#internal imports
import subuserlib.classes.registry, subuserlib.classes.repositories, subuserlib.classes.config, subuserlib.classes.installedImages, subuserlib.classes.dockerDaemon, subuserlib.test, subuserlib.paths

class User(object):
  """
  This class provides a "base" User object used by subuser.  This is the stem of a tree like data structure which holds all of the various objects owned by a given user:

   - settings
   - subusers
   - repository lists
  ect.

  You create a new User object by passing the home dir of the user.

  >>> import subuserlib.classes.user
  >>> u = subuserlib.classes.user.User("root","/root/")
  >>> u.homeDir
  '/root/'

  """
  name = None
  homeDir = None
  __config = None
  __registry = None
  __installedImages = None
  __dockerDaemon = None
  
  def __init__(self,name=None,homeDir=None):
    if os.path.exists(os.path.join(subuserlib.paths.getSubuserDir(),"installed-images.json")):
      sys.exit("""Hey, it looks like you are using an old version of subuser.  First of, thanks for being an early adopter!  That really means a lot to me :)  Subuser has recently undergone a major re-write.  Unfortunately, you'll have to set up everything all over again.  You can find your subuser home dirs in subuser/homes.  The new version of subuser keeps them in ~/.subuser/homes.  You can find out all about the different locations subuser serializes to by looking in the enw config.json file.  I hope I'll have some docs up soon at subuser.org.  Sorry for the inconvenience.

To disable this message delete your subuser/installed-programs.json file.
""")
    if name:
      self.name = name
    else:
      self.name = getpass.getuser()

    if homeDir:
      self.homeDir = homeDir
    else:
      if subuserlib.test.testing:
        self.homeDir = "/home/travis/test-home"
      else:
        self.homeDir = os.path.expanduser("~") 

  def getConfig(self):
    if self.__config == None:
      self.__config = subuserlib.classes.config.Config(self)
    return self.__config

  def getRegistry(self):
    if self.__registry == None:
      self.__registry = subuserlib.classes.registry.Registry(self)
    return self.__registry

  def getInstalledImages(self):
    if self.__installedImages == None:
      self.__installedImages = subuserlib.classes.installedImages.InstalledImages(self)
    return self.__installedImages

  def getDockerDaemon(self):
    if self.__dockerDaemon == None:
      self.__dockerDaemon = subuserlib.classes.dockerDaemon.DockerDaemon(self)
    return self.__dockerDaemon
