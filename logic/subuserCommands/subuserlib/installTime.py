#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import time
#internal imports
#import ...

installTimeFormat = "%Y-%m-%d-%H:%M"

def currentTimeString():
  """ Return the current time formatted as per spec. """
  return time.strftime(installTimeFormat ,time.gmtime(time.time()))