#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
#import ...
#internal imports
import SubuserProgram,registry

class InstalledSubuserProgram(SubuserProgram.SubuserProgram):
  installedName = None
  def __init__(self,installedName):
    _registry = registry.getRegistry()
    if not installedName in _registry:
      return None
    else:
      self.installedName = installedName
      self.sourceRepo = _registry[installedName]["source-repo"]
      self.sourceName = _registry[installedName]["source-name"]
      return self
