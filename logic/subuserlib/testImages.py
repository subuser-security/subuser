#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import pathConfig
#external imports
import os
import uuid
#internal imports
import subuserlib.verify
import subuserlib.subuser
import subuserlib.removeOldImages

def testImages(user,sourceRepoId,imageSourceNames,permissionsAccepter):
  """
  Build, run, and remove the given images.
  """
  subuserNames = []
  subuserNamePrefix = "!test-image-subuser-"
  # Build the images
  for imageSourceName in imageSourceNames:
    subuserName = subuserNamePrefix+imageSourceName
    subuserNames.append(subuserName)
    subuserlib.subuser.addFromImageSourceNoVerify(user,subuserName,user.getRegistry().getRepositories()[sourceRepoId][imageSourceName])
  subuserlib.verify.verify(user,subuserNames=subuserNames,permissionsAccepter=permissionsAccepter)
  user.getRegistry().commit()
  # Create a list of the names of the new subusers
  subuserNames = []
  for imageSourceName in imageSourceNames:
    subuserNames.append(subuserNamePrefix+imageSourceName)
  # Run the images
  for subuserName in subuserNames:
    arguments = raw_input("Running "+subuserName+" enter arguments and press enter to continue:")
    arguments = arguments.split(" ")
    subuser = user.getRegistry().getSubusers()[subuserName]
    if subuser.getPermissions()["executable"]:
      runtime = subuser.getRuntime(os.environ)
      if runtime:
        runtime.run(arguments)
  # Remove the subusers
  subuserlib.subuser.remove(user,subuserNames)
