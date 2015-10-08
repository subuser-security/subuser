#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
This is a PermissionAccepter object used to get user approval of permissions via the command line.
"""

#external imports
from collections import OrderedDict

# Python 2.x/Python 3 compatibility
try:
    input = raw_input
except NameError:
    raw_input = input

#internal imports
from subuserlib.classes.permissionsAccepters.permissionsAccepter import PermissionsAccepter
from subuserlib.classes.userOwnedObject import UserOwnedObject
import subuserlib.permissions
import subuserlib.subprocessExtras

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
      print(subuser.getName()+" would like to have the following permissions:")
      newDefaults.describe()
      createNewPermissions = True
    else:
      createNewPermissions = False
      (removedPermissions,additionsAndChanges) = subuserlib.permissions.compare(newDefaults = newDefaults, oldDefaults=oldDefaults, userApproved=userApproved)
      if additionsAndChanges == {} and removedPermissions == []:
        return
      if not additionsAndChanges == {}:
        print(subuser.getName()+" would like to add/change the following permissions:")
        for permission,value in additionsAndChanges.items():
          for line in subuserlib.permissions.descriptions[permission](value):
            print("   - "+line)
      if not removedPermissions == []:
        print(subuser.getName()+" no longer needs the following permissions:")
        for removedPermission in removedPermissions:
          for line in subuserlib.permissions.descriptions[removedPermission](oldDefaults[removedPermission]):
            print("   - "+line)
    options = OrderedDict([("A","Accept and apply changes")
                          ,("E","Apply changes and edit result")
                          ,("e","Ignore request and edit permissions by hand")])
    if createNewPermissions:
      del options["e"]
    for option,description in options.items():
      print(option+" - "+description)
    if self.getAllwaysAccept():
      print("A")
      choice = "A"
    else:
      choice = None
    while not choice in options:
      choice = raw_input("Please select an option:")
    if (choice == "A") or (choice == "E"):
      if createNewPermissions:
        subuser.createPermissions(newDefaults)
      else:
        subuser.getPermissions().applyChanges(removedPermissions,additionsAndChanges)
      subuser.getPermissions().save()
    if (choice == "E") or (choice == "e"):
      subuser.editPermissionsCLI()
