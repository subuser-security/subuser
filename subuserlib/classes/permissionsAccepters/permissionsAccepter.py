# -*- coding: utf-8 -*-
# pylint: disable=no-init,old-style-class

"""
This is a metaclass which describes the required methods that all permissions accepters must have.
"""

#external imports
import abc
#internal imports
#import ...

class PermissionsAccepter():
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def accept(self,oldDefaults,newDefaults,userApproved,exposeEntrypoints):
    """
    Prompt the user to either accept or edit the given permissions.
    Writes the new user approved permissions to the subuser's permissions.json file.
    userApproved may be None if no permissions have been accepted yet.
    """
    pass
