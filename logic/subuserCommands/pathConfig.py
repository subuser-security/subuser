#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import sys
import os
import inspect
import site

def getSubuserDir():
  """ Get the toplevel directory for subuser. """
  return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))) # BLEGH!

sys.path.insert(0,os.path.join(getSubuserDir(),"logic"))
