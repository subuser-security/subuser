# -*- coding: utf-8 -*-

"""
This is a PermissionAccepter object used to get user approval of permissions via the command line.
"""

#external imports
from collections import OrderedDict
#internal imports
from subuserlib.classes.permissionsAccepters.permissionsAccepter import PermissionsAccepter
from subuserlib.classes.userOwnedObject import UserOwnedObject
import subuserlib.permissions
import subuserlib.print

class AcceptPermissionsAtCLI(PermissionsAccepter,UserOwnedObject):
  def __init__(self,user,alwaysAccept = False):
    self.alwaysAccept = alwaysAccept
    UserOwnedObject.__init__(self,user)

  def accept(self,subuser,newDefaults,oldDefaults,userApproved):
    if userApproved is None:
      subuserlib.print.printWithoutCrashing(subuser.name+u": would like to have the following permissions:")
      newDefaults.describe()
      createNewPermissions = True
    else:
      createNewPermissions = False
      (removedPermissions,additionsAndChanges) = subuserlib.permissions.compare(newDefaults = newDefaults, oldDefaults=oldDefaults, userApproved=userApproved)
      if additionsAndChanges == {} and removedPermissions == [] and not subuser.wereEntryPointsExposedThisRun():
        return
      if not additionsAndChanges == {}:
        subuserlib.print.printWithoutCrashing(subuser.name+" would like to add/change the following permissions:")
        subuserlib.print.printWithoutCrashing(subuserlib.permissions.getDescription(additionsAndChanges))
      if not removedPermissions == []:
        subuserlib.print.printWithoutCrashing("")
        subuserlib.print.printWithoutCrashing(subuser.name+" no longer needs the following permissions:")
        removedPermisisonsDict = {}
        for removedPermission in removedPermissions:
          removedPermisisonsDict[removedPermission] = oldDefaults[removedPermission]
        subuserlib.print.printWithoutCrashing(subuserlib.permissions.getDescription(removedPermisisonsDict))
      if "entrypoints" in additionsAndChanges and subuser.entryPointsExposed:
        subuserlib.print.printWithoutCrashing(subuser.name+" would like to expose the following entrypoints to the system PATH:")
        for entrypoint in additionsAndChanges["entrypoints"].keys():
          subuserlib.print.printWithoutCrashing(entrypoint)
      if subuser.wereEntryPointsExposedThisRun():
        if subuser.permissions["entrypoints"]:
          subuserlib.print.printWithoutCrashing(subuser.name+" would like to expose the following entrypoints to the system PATH:")
          for entrypoint in subuser.permissions["entrypoints"].keys():
            subuserlib.print.printWithoutCrashing(entrypoint)
        else:
          subuserlib.print.printWithoutCrashing("Entrypoints marked to be exposed, but nothing to expose.")
          if additionsAndChanges == {} and removedPermissions == []:
            return
    options = OrderedDict([("A","Accept and apply changes")
                          ,("E","Apply changes and edit result")
                          ,("e","Ignore request and edit permissions by hand")
                          ,("r","Reject permissions.")])
    if createNewPermissions:
      del options["e"]
    for option,description in options.items():
      subuserlib.print.printWithoutCrashing(option+" - "+description)
    if self.alwaysAccept:
      subuserlib.print.printWithoutCrashing("A")
      choice = "A"
    else:
      choice = None
    while not choice in options:
      try:
        choice = input("Please select an option:")
      except EOFError:
        choice = "r"
    if (choice == "A") or (choice == "E"):
      if createNewPermissions:
        subuser.createPermissions(newDefaults)
      else:
        subuser.permissions.applyChanges(removedPermissions,additionsAndChanges)
      subuser.permissions.save()
    if (choice == "E") or (choice == "e"):
      subuser.editPermissionsCLI()
    if choice == "r":
      if createNewPermissions:
        subuser.createPermissions(subuserlib.permissions.load(permissionsString="{}",logger=self.user.registry))
        subuser.permissions.save()
