#!/usr/bin/python
import sys,subprocess
sys.path.append("../../logic/subuserCommands")
import subuserlib.commands

builtInCommands = subuserlib.commands.getBuiltInSubuserCommands()

for command in builtInCommands:
  with open(command+".rst","w") as command_file:
    commandDocs = command + "\n"+("="*len(command))+"\n"
    commandHelpOutput = subprocess.check_output(["../../logic/subuser",command,"--help"])
    commandDocs += commandHelpOutput.replace("\n\n    $","\n::\n\n    $")
    command_file.write(commandDocs)

