#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

# NOTE: This file exists only to provide some things that are also int paths, to modules that cannot import paths due to dependency import order issues.  If in doubt import and use paths and not basicPaths!

#external imports
import os,inspect
#internal imports
#import ...
home = os.path.expanduser("~") 

def getSubuserDir():
  """ Get the toplevel directory for subuser. """
  return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))) # BLEGH!

