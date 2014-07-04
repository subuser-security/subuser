#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
#import ...
#internal imports
#import ...

class SubuserProgram:
  sourceName = None
  sourceRepo = None
  def __init__(self,sourceRepo,sourceName):
    self.sourceRepo=sourceRepo
    self.sourceName=sourceName
    return self