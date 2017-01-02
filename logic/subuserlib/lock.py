# -*- coding: utf-8 -*-

"""
File locking helper functions. Originally taken from http://stackoverflow.com/questions/5255220/fcntl-flock-how-to-implement-a-timeout
"""

#external imports
import os
#internal imports
#import ...
import signal, errno
from contextlib import contextmanager
import fcntl

@contextmanager
def wrapTimeout(seconds):
  def timeout_handler(signum, frame):
    pass

  original_handler = signal.signal(signal.SIGALRM, timeout_handler)

  try:
    signal.alarm(seconds)
    yield
  finally:
    signal.alarm(0)
    signal.signal(signal.SIGALRM, original_handler)

def getLock(fd,timeout=None):
  if not timeout is None:
    with wrapTimeout(timeout):
      return getLock(fd)
  else:
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd
