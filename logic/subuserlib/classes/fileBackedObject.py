#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
# pylint: disable=no-init,old-style-class

"""
If an object has persistant state which needs to be serialzed to disk, that object should be backed by a file.
"""

#external imports
import abc
#internal imports
#import ...

class FileBackedObject():
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def save(self):
    """ Serialize the object to it's appropriate location on disk. """
    pass
