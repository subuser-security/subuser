# -*- coding: utf-8 -*-

"""
Helper functions for running foreign executables.
"""

#external imports
import subprocess
import os
import tempfile
#internal imports
import subuserlib.test

def call(args,cwd=None):
  """
  Same as subprocess.call except here you can specify the cwd.

  Returns subprocess's exit code.
  """
  process = subprocess.Popen(args,cwd=cwd)
  (stdout,stderr) = process.communicate()
  return process.returncode

def callBackground(args,cwd=None,suppressOutput=True,collectStdout=False,collectStderr=False):
  """
  Same as subprocess.call except here you can specify the cwd.
  Returns imediately with the subprocess
  """
  stdout = None
  stderr = None

  if suppressOutput:
    devnull = open(os.devnull,"a")
    stdout = devnull
    stderr = devnull

  if collectStdout:
    temp_stdout = tempfile.TemporaryFile(mode="r")
    stdout = temp_stdout.fileno()
  if collectStderr:
    temp_stderr = tempfile.TemporaryFile(mode="r")
    stderr = temp_stderr.fileno()

  process = subprocess.Popen(args,cwd=cwd,stdout=stdout,stderr=stderr,close_fds=True)

  if collectStdout:
    process.stdout_file = temp_stdout
  if collectStderr:
    process.stderr_file = temp_stderr

  return process

def callCollectOutput(args,cwd=None):
  """
  Run the command and return a tuple with: (returncode,the output to stdout as a string,stderr as a string).
  """
  process = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=cwd)
  (stdout,stderr) = process.communicate()
  return (process.returncode,stdout.decode("utf-8"),stderr.decode("utf-8"))

