#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import time

installTimeFormat = "%Y-%m-%d-%H:%M"

def currentTimeString():
  """ Return the current time formatted as per spec. """
  return time.strftime(installTimeFormat ,time.gmtime(time.time()))
