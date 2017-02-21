#!/usr/bin/python3
import sys,subprocess
sys.path.append("../../logic")
import subuserlib.permissions

with open("permissions-dot-json-file-format.rst","w") as permissions_format_file:
  permissions_format_file.write(subuserlib.permissions.getDocs())
