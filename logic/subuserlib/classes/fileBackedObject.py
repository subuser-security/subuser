# -*- coding: utf-8 -*-
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
