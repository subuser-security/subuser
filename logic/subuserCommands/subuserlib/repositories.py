#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

# TODO, refactor by putting helper functions for both repositories.py and configs.py in one place.

#external imports
import os,inspect,json,collections,sys
#internal imports
import subuserlib.loadMultiFallbackJsonConfigFile



def getRepositories():
  """ Returns a dictionary of repositories used by subuser. """
  
  return repositories
