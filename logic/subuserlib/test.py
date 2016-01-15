# -*- coding: utf-8 -*-

"""
This is a "magic" module used to transmit the global testing flag, so modules will know if they are being tested.  (Some modules use mock objects, others don't do certain actions during testing.)
"""

#external imports
import os
#internal imports
#import ...

if "SUBUSER_TESTING" in os.environ:
  testing = True
  import os
  homeDir = os.getcwd()
  hashtestDir = homeDir+"/hashtest"
  def getUser():
    from subuserlib.classes.user import User
    return User(homeDir=homeDir)
else:
  testing = False
