#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import abc
#internal imports
#import ...

class Describable(object):
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def describe():
    """ Print out a human readable description of the object. """
    pass
