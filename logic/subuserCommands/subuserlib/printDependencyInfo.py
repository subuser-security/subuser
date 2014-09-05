#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import json
#internal imports
import registry

def printDependencyTables(images):
  dependencyTable = registry.getDependencyTable(images, useHasExecutable=False, sortLists=True)
  for image in dependencyTable.keys():
    print(image+":")
    print("    required-by: " + ", ".join(dependencyTable[image]["required-by"]))
    print("    depends-on: " + ", ".join(dependencyTable[image]["depends-on"]))

def printDependencyTableJson(images):
  dependencyTable =registry.getDependencyTable(images, useHasExecutable=False, sortLists=True)
  print(json.dumps(dependencyTable))

def printDependencyTrees(imageList):
  for image in imageList:
    treeString = ''
    for index, dependency in enumerate(registry.getDependencyTree(image)):
      if index > 0:
        treeString = ''.join([treeString, '  ' * index, '|__', dependency, '\n'])
      else:
        treeString = ''.join([treeString, dependency, '\n'])
  
    print(treeString)
  
  
def printDependencyInfo(imageList,format):
  if format == 'table':
    printDependencyTables(imageList)
  elif format == 'tree':
    printDependencyTrees(imageList)
  elif format == 'json':
    printDependencyTableJson(imageList)