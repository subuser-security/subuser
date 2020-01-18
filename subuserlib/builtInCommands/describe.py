#!/usr/bin/python3
# -*- coding: utf-8 -*-

#external imports
#import ...
#internal imports
import subuserlib.builtInCommands.list

@subuserlib.profile.do_cprofile
def runCommand(sysargs):
  subuserlib.builtInCommands.list.runCommand(sysargs)
