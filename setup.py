#!/usr/bin/python3
import setuptools
import os
import inspect

def readme():
  with open("README.rst") as f:
    return f.read()

def version():
  with open("VERSION") as f:
    return f.read().strip()

commands = ["logic/subuser","logic/execute-json-from-fifo"]

setuptools.setup(
  name="subuser",
  version=version(),
  description="subuser - a program which helps you run other programs in containers, securely and portably.",
  long_description=readme(),
  classifiers=[
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
    "Programming Language :: Python :: 3.0",
    ],
  keywords="subuser Docker containers security portability",
  url="http://subuser.org",
  author="Timothy Hobbs",
  author_email="timothy@hobbs.cz",
  license="LGPL-3.0",
  packages=["subuserlib","subuserlib.classes","subuserlib.builtInCommands","subuserlib.classes.docker","subuserlib.classes.subuserSubmodules","subuserlib.classes.subuserSubmodules.run","subuserlib.classes.permissionsAccepters"],
  package_dir={"subuserlib": "logic/subuserlib",
               "subuserlib.builtInCommands":"logic/subuserlib/builtInCommands",
               "subuserlib.classes":"logic/subuserlib/classes",
               "subuserlib.classes.docker":"logic/subuserlib/classes/docker",
               "subuserlib.classes.subuserSubmodules":"logic/subuserlib/classes/subuserSubmodules",
               "subuserlib.classes.subuserSubmodules.run":"logic/subuserlib/classes/subuserSubmodules/run",
               "subuserlib.classes.permissionsAccepters":"logic/subuserlib/classes/permissionsAccepters"},
  package_data={'subuserlib': ['data/*']},
  scripts=commands,
  include_package_data=True,
  zip_safe=False)
