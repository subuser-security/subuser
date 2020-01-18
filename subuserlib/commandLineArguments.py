# -*- coding: utf-8 -*-
"""
This module contains configurations for C{optparse}.
"""

#external imports
import optparse
#internal imports
#import ...

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
