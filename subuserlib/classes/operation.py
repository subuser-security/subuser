# -*- coding: utf-8 -*-

"""
Each time you run a command such as `subuser subuser add foo xterm` you are preforming an operation which modifies the subuser registry and which builds images. Many of the steps are repeated for each operation and many of the configuration options are global to all operations. This class defines an operation "super-object" which attempts to collate all of these parameters in one place.
"""

#external imports
import json
#internal imports
from subuserlib.classes.userOwnedObject import UserOwnedObject
from subuserlib.classes.permissionsAccepters.acceptPermissionsAtCLI import AcceptPermissionsAtCLI

class Operation(UserOwnedObject):
  def __init__(self,user):
    UserOwnedObject.__init__(self,user)
    self.permissionsAccepter = AcceptPermissionsAtCLI(user)
    self.prompt = True
    self.checkForUpdatesExternally=False
    self.subusers=[] # which subusers are we operating on
    self.useCache=False
    self.build=True

  def loadSubusersByName(self,names):
   for name in names:
     if not name in self.user.registry.subusers:
       raise LookupError("Subuser "+name+" does not exist.")
     else:
       self.subusers.append(self.user.registry.subusers[name])

