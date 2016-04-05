#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This file is copyright Timothy Hobbs
# And is released under the GPLv3 license

"""
This is a very simple script which executes commands passed as JSON to a given named pipe.

To launch this script run:

$ ./execute-json-from-fifo.py PATH_TO_NAMED_PIPE

The protocol is as follows:

{
  "command":["echo","some","command"],
  "stdin":"path",
  "stdout":"path",
  "stderr":"path",
  "cwd":"path"
  "env":{"ENVVAR":"value"}
}

``stdin``,``stdout``,``stderr``,``cwd`` and ``env`` are all optional.

Passing ``["exit"]`` to command stops the script.

"""

import json
import subprocess
import fileinput
import sys

while True:
  with open(sys.argv[1],"r") as fd:
    for line in fd:
      rpc = json.loads(line)
      if rpc["command"] == ["exit"]:
        sys.exit()
      if "stdin" in rpc:
        stdin = open(rpc["stdin"],"r+")
      else:
        stdin = open("/dev/null","r")
      if "stdout" in rpc:
        stdout = open(rpc["stdout"],"w")
      else:
        stdout = open("/dev/null","w")
      if "stderr" in rpc:
        stderr = open(rpc["stderr"],"w")
      else:
        stderr = open("/dev/null","w")
      cwd = None
      if "cwd" in rpc:
        cwd = rpc["cwd"]
      env = None
      if "env" in rpc:
        env = rpc["env"]
      subprocess.Popen(rpc["command"],stdin=stdin,stdout=stdout,stderr=stderr,cwd=cwd,env=env,close_fds=True)
