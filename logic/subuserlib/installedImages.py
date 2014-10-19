#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
This is used for deep inspection of which images are installed in Docker and what their dependencies are.
"""

#external imports
#import ...
#internal imports
#import ...

def getImageLineageInLayers(user,imageId):
  """
  Return the list(lineage) of id of Docker image layers which goes from a base image to this image including all of the image's ancestors in order of dependency.
  If imageId is None or is not installed, return [].
  """
  imageProperties = user.getDockerDaemon().getImageProperties(imageId)
  if imageProperties == None:
    return []
    #sys.exit("Failed to get properties of image "+imageId)
  if not imageProperties["Parent"] == "":
    return getImageLineageInLayers(user,imageProperties["Parent"]) + [imageId]
  else:
    return [imageId]

def getImageLineage(user,imageId):
  """
  Return the list(lineage) of InstalledImages which goes from a base image to this image including all of the image's ancestors in order of dependency.
  If imageId is None, return [].
  """
  if imageId == None:
    return []

  lineage = []
  dockerImageLayers = getImageLineageInLayers(user,imageId)
  for dockerImageLayer in dockerImageLayers:
    if dockerImageLayer in user.getInstalledImages():
      lineage.append(user.getInstalledImages()[dockerImageLayer])
  return lineage
