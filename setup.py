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
  packages=setuptools.find_packages(),
  package_data={'subuserlib': ['data/*']},
  scripts=commands,
  setup_requires=['wheel'],
  include_package_data=True,
  zip_safe=False)
