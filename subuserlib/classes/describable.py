# -*- coding: utf-8 -*-

"""
If you want to print a description of an object to standard output, make that object describable.
"""

#external imports
import abc
#internal imports
#import ...

class Describable(object):
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def describe(self):
    """ Print out a human readable description of the object. """
    pass
