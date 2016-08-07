# -*- coding: utf-8 -*-

"""
This module provides the usefull function C{which} which allows us to find the full path of a given executable and determine if an executable is present on the given system.
"""

#external imports
import os
#internal imports
#import ...

def isExecutable(fpath):
  """
  Returns true if the given filepath points to an executable file.
  """
  return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

programs = {}
# Origonally taken from: http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program,excludeDir=None):
  """
  @type program: string
  @param program: The short name of the executable.  Ex: "vim"
  @rtype: str or None
  @return: Returns the full path of a given executable.  Or None, of the executable is not present on the given system.
  """
  global programs
  try:
    return programs[(program,excludeDir)]
  except KeyError:
    pass
  fname = program
  def matchesImage(path):
    fpath,fname = os.path.split(path)
    return program == fname and not fpath == excludeDir
  program = queryPATH(matchesImage)
  programs[(program,excludeDir)] = program
  return program

def queryPATH(test,list=False):
  """
  Search the PATH for an executable.
  """
  paths = []
  for path in os.environ["PATH"].split(os.pathsep):
    path = path.strip('"')
    if os.path.exists(path):
      for fileInPath in os.listdir(path):
        exeFile = os.path.join(path, fileInPath)
        if isExecutable(exeFile):
          if test(exeFile):
            if list:
              paths.append(exeFile)
            else:
              return exeFile
  if list:
    return paths
  else:
    return None
