#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import paths

def available(programName):
 """ Returns True if the program is available for instalation. """
 import os
 return os.path.exists(paths.getProgramSrcDir(programName))
