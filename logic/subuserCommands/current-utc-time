#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import sys,optparse
#internal imports
import subuserlib.installTime,subuserlib.commandLineArguments

def parseCliArgs():
  usage = "usage: subuser %prog"
  description = """ Display the current time in properly formatted utc.  Useful for setting the last-update-time attribute in permissions.json

"""
  parser = optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  return parser.parse_args()

parseCliArgs()
print(subuserlib.installTime.currentTimeString())

