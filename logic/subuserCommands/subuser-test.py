#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pathConfig
#external imports
import sys
import os
import io
import subprocess
#internal imports
import subuserlib.docker
import subuserlib.paths
import subuserlib.paths

def addSubuserIfNoneExists(name,source):
  command = [os.path.join(subuserlib.paths.getSubuserDir(),"logic","subuser"),"list","subusers","--internal"]
  if not name in subprocess.check_output(command).decode():
    command = [os.path.join(subuserlib.paths.getSubuserDir(),"logic","subuser"),"subuser","add",name,source,"--force-internal"]
    subprocess.call(command)

if "--help" in sys.argv:
  print("""
To launch the test suit, run ``subuser test``. The first time you run it, instalation of the test suit will take a long time, so be patient.

You can also run launch the xpra bridge tests by running ``subuser test xpra-bridge``.

""")
  sys.exit()
elif "xpra-bridge" in sys.argv:
  xtermSubuserName = "!xterm-subuser-for-xpra-bridge-test"
  addSubuserIfNoneExists(xtermSubuserName,"xterm@default")
  pid = os.fork()
  if pid:
    counter = "a"
  else:
    counter = "b"
  for i in range(1,6):
    print(counter+" "+str(i))
    command = [os.path.join(subuserlib.paths.getSubuserDir(),"logic","subuser"),"run",xtermSubuserName]
    subprocess.call(command)
elif "doctest" in sys.argv:
  #import locale
  #locale.setlocale(locale.LC_ALL, '')
  import subuserlib.docker
  import doctest
  if not "--travis" in sys.argv:
    subuserDir = "/pwd"
  else:
    subuserDir = subuserlib.paths.getSubuserDir()
  # classes
  import subuserlib.classes.user
  import subuserlib.classes.subuser
  import subuserlib.classes.fileStructure
  import subuserlib.classes.gitRepository
  # libs
  import subuserlib.resolve
  import subuserlib.permissions
  # commands
  list = __import__("subuser-list")
  version = __import__("subuser-version")
  describe = __import__("subuser-describe")
  repository = __import__("subuser-repository")
  subuser = __import__("subuser-subuser")
  update = __import__("subuser-update")
  print_dependency_info = __import__("subuser-print-dependency-info")
  remove_old_images = __import__("subuser-remove-old-images")
  modules = [
    # classes
    subuserlib.classes.user
    ,subuserlib.classes.subusers
    # subuserlib modules
    ,subuserlib.permissions
    ,subuserlib.resolve
    # subuser commands
    ,list
    ,version
    ,describe
    ,print_dependency_info
    ,remove_old_images
    ,repository
    ,subuser
    ,update
    ]
  localOnlyModules = [ # These don't work with travis for some reason...
    subuserlib.classes.fileStructure
    ,subuserlib.classes.gitRepository]
  if not "--travis" in sys.argv:
    modules.extend(localOnlyModules)
  for module in modules:
    print("Testing module: " + module.__name__)
    optionflags = 0
    (failures,_) = doctest.testmod(module,optionflags=optionflags)
    if failures:
      sys.exit(failures)
  print("Tests passed.")
else:
  if not "logic" in os.listdir(os.getcwd()):
    sys.exit("You must first cd to the subuser source directory to test subuser.")
  command = [os.path.join(subuserlib.paths.getSubuserDir(),"logic","subuser"),"dev","texttest"]
  subprocess.call(command)
