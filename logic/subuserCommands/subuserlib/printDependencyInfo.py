#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import json
#internal imports
import registry

def printDependencyTables(programs):
  dependencyTable = registry.getDependencyTable(programs, useHasExecutable=False, sortLists=True)
  for program in dependencyTable.keys():
    print(program+":")
    print("    required-by: " + ", ".join(dependencyTable[program]["required-by"]))
    print("    depends-on: " + ", ".join(dependencyTable[program]["depends-on"]))

def printDependencyTableJson(programs):
  dependencyTable =registry.getDependencyTable(programs, useHasExecutable=False, sortLists=True)
  print(json.dumps(dependencyTable))

def printDependencyTrees(programList):
  for program in programList:
    treeString = ''
    for index, dependency in enumerate(registry.getDependencyTree(program)):
      if index > 0:
        treeString = ''.join([treeString, '  ' * index, '|__', dependency, '\n'])
      else:
        treeString = ''.join([treeString, dependency, '\n'])
  
    print(treeString)
  
  
def printDependencyInfo(programList,format):
  if format == 'table':
    printDependencyTables(programList)
  elif format == 'tree':
    printDependencyTrees(programList)
  elif format == 'json':
    printDependencyTableJson(programList)