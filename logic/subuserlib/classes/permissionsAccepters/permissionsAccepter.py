#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
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
  def accept(self,oldDefaults,newDefaults,userApproved):
    """
    Prompt the user to either accept or edit the given permissions.
    Writes the new user approved permissions to the subuser's permissions.json file.
    userApproved may be None if no permissions have been accepted yet.
    """
    pass

