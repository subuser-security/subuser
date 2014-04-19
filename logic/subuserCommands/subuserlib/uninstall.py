#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import sys,os,subprocess

import paths
import registry
import dockerImages
import docker

def uninstall(programName):
  print("Uninstalling "+programName)
  if dockerImages.isProgramsImageInstalled(programName):
    while not docker.runDocker(["rmi","subuser-"+programName]) == 0:
      if not raw_input("Once you have solved the problem either type [y] to continue, or [q] to exit: ") == 'y':
        sys.exit()
  if os.path.exists(paths.getExecutablePath(programName)):
    os.remove(paths.getExecutablePath(programName))

  registry.unregisterProgram(programName)
  programHomeDir=paths.getProgramHomeDirOnHost(programName)
  if os.path.exists(programHomeDir):
    print("The program has been uninstalled but it's home directory remains:")
    print(programHomeDir)
  print(programName+" uninstalled successfully.")