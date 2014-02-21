#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import paths
import os

def available(programName):
  """ Returns True if the program is available for instalation. """
  return os.path.exists(paths.getProgramSrcDir(programName))

def getAvailablePrograms():
  """ Returns a list of program's available for instalation. """
  availableProgramsPath = paths.getAvailableProgramsPath()
  return os.listdir(availableProgramsPath)

def getAvailableProgramsText(addNewLine=False, indentSpaces=0):
  """ Returns a string representing a sorted list of available program names.
  Arguments:
   - indentSpaces: can be set for nicer output especially togehter with: addNewLine
   - addNewLine: if True each installed program's name starts at a new line
  
  e.g.: `print(getAvailableProgramsText(addNewLine=True, indentSpaces=3))`
  """
  outText = ''
  indentionString = ''
  if indentSpaces > 0:
    indentionString = ' ' * indentSpaces
    
  if addNewLine:
    for program in sorted(getAvailablePrograms()):
      outText = ''.join([outText, indentionString, program, '\n'])
  else:
    outText = indentionString + ' '.join(sorted(getAvailablePrograms()))
  return outText
