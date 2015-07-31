#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import pathConfig
#external imports
import os,uuid
#internal imports
import subuserlib.verify,subuserlib.subuser,subuserlib.removeOldImages

def testImages(user,sourceRepoId,imageSourceNames):
  """
  Build, run, and remove the given images.
  """
  subuserNamePrefix = "test-image-subuser" + str(uuid.uuid4())
  # Build the images
  for imageSourceName in imageSourceNames:
    subuserlib.subuser.addFromImageSourceNoVerify(user,subuserNamePrefix+imageSourceName,user.getRegistry().getRepositories()[sourceRepoId][imageSourceName])
  subuserlib.verify.verify(user)
  # Create a list of the names of the new subusers
  subuserNames = []
  for imageSourceName in imageSourceNames:
    subuserNames.append(subuserNamePrefix+imageSourceName)
  # Run the images
  for subuserName in subuserNames:
    raw_input("Running "+subuserName+" press enter to continue:")
    subuser = user.getRegistry().getSubusers()[subuserName]
    if subuser.getPermissions()["executable"]:
      runtime = subuser.getRuntime(os.environ)
      if runtime:
        runtime.run([])
  # Remove the subusers
  subuserlib.subuser.remove(user,subuserNames)

