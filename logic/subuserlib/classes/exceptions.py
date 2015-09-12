#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
This is a collection of exceptions which are raised throughout the sourcecode.
"""

#external imports
#import ...
#internal imports
#import ..

class ImageBuildException(Exception):
  """
  This exception is raised any time an image fails to build and subuser is not at fault.
  """
  pass
