#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import sys
import subprocess
import availablePrograms

def subprocessCheckedCall(args, **kwargs):
 """ simplify subprocess.check_call in other code
 """
 try:
  subprocess.check_call(args, **kwargs)
 except subprocess.CalledProcessError:
  sys.exit('Command failed: %s' % ' '.join(args))

def checkExitNoneAvailableProgram(programName, additionalInfo=''):
 """ check a none-available program is requested in such case give the user some helpful feedback
 and exit.
 """
 if not availablePrograms.available(programName):
  print("<%s>: not an available subuser-program." % programName)
  print("\nAvailable subuser-programs are: ")
  print(' '.join(sorted([program for program in availablePrograms.getAvailablePrograms()])))
  print('\n'+additionalInfo)
  sys.exit()
