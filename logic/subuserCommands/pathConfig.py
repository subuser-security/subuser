#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import inspect
import site

def getSubuserDir():
  """ Get the toplevel directory for subuser. """
  return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))) # BLEGH!

sys.path.insert(0,os.path.join(getSubuserDir(),"logic"))
