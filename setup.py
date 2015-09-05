import setuptools
import os
import inspect

def readme():
  with open("README.md") as f:
    return f.read()


pathToThisSourceFile = os.path.abspath(inspect.getfile(inspect.currentframe()))

commands = [os.path.join("logic","subuserCommands",command) for command in os.listdir(os.path.join(os.path.dirname(pathToThisSourceFile),"logic","subuserCommands")) if command.startswith("subuser-") and command.endswith(".py")]
scripts = ["logic/subuser"]+commands

setuptools.setup(
  name="subuser",
  version="0.4-dev",
  description="subuser - a program which helps you run other programs in containers, securly and portably.",
  long_description=readme(),
  classifiers=[
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.0",
    ],
  keywords="subuser Docker containers security portability",
  url="http://subuser.org",
  author="Timothy Hobbs",
  author_email="timothy@hobbs.cz",
  license="LGPLv3",
  packages=["subuserlib","subuserlib.classes","subuserlib.classes.docker","subuserlib.classes.subuserSubmodules","subuserlib.classes.subuserSubmodules.run","subuserlib.classes.permissionsAccepters"],
  package_dir={"subuserlib": "logic/subuserlib",
               "subuserlib.classes":"logic/subuserlib/classes",
               "subuserlib.classes.docker":"logic/subuserlib/classes/docker",
               "subuserlib.classes.subuserSubmodules":"logic/subuserlib/classes/subuserSubmodules",
               "subuserlib.classes.subuserSubmodules.run":"logic/subuserlib/classes/subuserSubmodules/run",
               "subuserlib.classes.permissionsAccepters":"logic/subuserlib/classes/permissionsAccepters"},
  package_data={'subuserlib': ['data/*']},
  scripts=scripts,
  include_package_data=True,
  zip_safe=False)
