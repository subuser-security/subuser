#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
"""
This module contains configurations for C{optparse}.
"""

#external imports
import optparse
#internal imports
#import ...

# Note the --from-cache option is not currently supported.  A pull request implementing this flag for "update all", "repair" and "subuser add" would be greatly appreciated :) .
def advancedInstallOptionsGroup(parser):
  """
  These are advanced installation options shared by several commands, install, update ect.
  """
  advancedOptions = optparse.OptionGroup(parser,"Advanced Options")
  advancedOptions.add_option("--from-cache",action="store_true",default=False,dest="useCache",help="""Use the layer cache while building the image's image.  This is dangerous and therefore dissabled by default.  The layer cache caches certain commands used to build layers.  Since some commands such as "apt-get update" should not be cached we turn this option off by default.""")
  return advancedOptions

class HelpFormatterThatDoesntReformatDescription (optparse.HelpFormatter):
  """
  Format help with indented section bodies but don't reformat the description.
  """
  def __init__(self, indent_increment=2, max_help_position=24, width=None,short_first=1):
    optparse.HelpFormatter.__init__(self, indent_increment, max_help_position, width, short_first)

  def format_usage(self, usage):
    return optparse._("Usage: %s\n") % usage

  def format_heading(self, heading):
    return "%*s%s:\n" % (self.current_indent, "", heading)

  def format_description(self, description):
    return description
