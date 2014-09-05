#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import sys,os,subprocess
#internal imports
import paths,registry,dockerImages,docker

def uninstall(imageName):
  print("Uninstalling "+imageName)
  if dockerImages.isImagesImageInstalled(imageName):
    while not docker.runDocker(["rmi","subuser-"+imageName]) == 0:
      if not raw_input("Once you have solved the problem either type [y] to continue, or [q] to exit: ") == 'y':
        sys.exit()
  if os.path.exists(paths.getExecutablePath(imageName)):
    os.remove(paths.getExecutablePath(imageName))

  registry.unregisterImage(imageName)
  imageHomeDir=paths.getImageHomeDirOnHost(imageName)
  if os.path.exists(imageHomeDir):
    print("The image has been uninstalled but it's home directory remains:")
    print(imageHomeDir)
  print(imageName+" uninstalled successfully.")