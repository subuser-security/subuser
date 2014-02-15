#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import sys
import subprocess

def subprocessCheckedCall(args, **kwargs):
 """ simplify subprocess.check_call in other code
 """
 try:
  subprocess.check_call(args, **kwargs)
 except subprocess.CalledProcessError:
  sys.exit('Command failed: %s' % ' '.join(args))
