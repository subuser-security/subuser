# -*- coding: utf-8 -*-

"""
Profiling helper function. Taken from: https://zapier.com/engineering/profiling-python-boss/
"""

#external imports
import cProfile
import os
#internal imports
#import ...

def do_cprofile(func):
  if not "SUBUSER_RUN_PROFILER" in os.environ:
    return func
  def profiled_func(*args, **kwargs):
    profile = cProfile.Profile()
    try:
      profile.enable()
      result = func(*args, **kwargs)
      profile.disable()
      return result
    finally:
      profile.print_stats(sort='cumtime')
  return profiled_func
