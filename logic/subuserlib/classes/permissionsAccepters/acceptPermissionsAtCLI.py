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
    self.__alwaysAccept = alwaysAccept
    UserOwnedObject.__init__(self,user)

  def getAllwaysAccept(self):
    """
    Should the accepter accept the permissions/changes without actually prompting the users?
    """
    return self.__alwaysAccept

  def accept(self,subuser,newDefaults,oldDefaults,userApproved):
    if userApproved is None:
      subuserlib.print.printWithoutCrashing(subuser.getName()+u": would like to have the following permissions:")
      newDefaults.describe()
      createNewPermissions = True
    else:
      createNewPermissions = False
      (removedPermissions,additionsAndChanges) = subuserlib.permissions.compare(newDefaults = newDefaults, oldDefaults=oldDefaults, userApproved=userApproved)
      if additionsAndChanges == {} and removedPermissions == [] and not subuser.wereEntryPointsExposedThisRun():
        return
      if not additionsAndChanges == {}:
        subuserlib.print.printWithoutCrashing(subuser.getName()+" would like to add/change the following permissions:")
        for permission,value in additionsAndChanges.items():
          for line in subuserlib.permissions.descriptions[permission](value):
            subuserlib.print.printWithoutCrashing("   - "+line)
      if not removedPermissions == []:
        subuserlib.print.printWithoutCrashing("")
        subuserlib.print.printWithoutCrashing(subuser.getName()+" no longer needs the following permissions:")
        for removedPermission in removedPermissions:
          for line in subuserlib.permissions.descriptions[removedPermission](oldDefaults[removedPermission]):
            subuserlib.print.printWithoutCrashing("   - "+line)
      if "entrypoints" in additionsAndChanges and subuser.areEntryPointsExposed():
        subuserlib.print.printWithoutCrashing(subuser.getName()+" would like to expose the following entrypoints to the system PATH:")
        for entrypoint in additionsAndChanges["entrypoints"].keys():
          subuserlib.print.printWithoutCrashing(entrypoint)
      if subuser.wereEntryPointsExposedThisRun():
        if subuser.getPermissions()["entrypoints"]:
          subuserlib.print.printWithoutCrashing(subuser.getName()+" would like to expose the following entrypoints to the system PATH:")
          for entrypoint in subuser.getPermissions()["entrypoints"].keys():
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
    if self.getAllwaysAccept():
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
        subuser.getPermissions().applyChanges(removedPermissions,additionsAndChanges)
      subuser.getPermissions().save()
    if (choice == "E") or (choice == "e"):
      subuser.editPermissionsCLI()
    if choice == "r":
      if createNewPermissions:
        subuser.createPermissions(subuserlib.permissions.load(permissionsString="{}"))
        subuser.getPermissions().save()
