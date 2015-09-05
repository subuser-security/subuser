#!/usr/bin/python
import sys,subprocess
sys.path.append("../../logic")
import subuserlib.commands

builtInCommands = subuserlib.commands.getBuiltIn()

for command in builtInCommands:
  with open(command+".rst","w") as command_file:
    commandDocs = command + "\n"+("="*len(command))+"\n"
    print("Collecting help for:"+command)
    commandHelpOutput = subprocess.check_output(["../../logic/subuser",command,"--help"])
    commandDocs += commandHelpOutput.replace("\n\n    $","\n::\n\n    $")
    command_file.write(commandDocs)

with open("index.rst",mode="w") as index:
  with open("index.rst.head",mode="r") as indexHead:
    index.write(indexHead.read())
  for command in builtInCommands:
    index.write("  "+command+"\n")
  index.write("\n")
    
