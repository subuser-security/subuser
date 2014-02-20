#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
import subprocess
import availablePrograms
import utils
import json
import sys

def askToInstallProgram(programName):
  """ Asks the user if they want to install the given program.  If they say yes, install it, if they decline exit."""
  if not availablePrograms.available(programName):
    print(programName+" does not exist.")
    exit()
  if raw_input(programName+" is not installed. Do you want to install it now [y/n]?") == "y":
    utils.subprocessCheckedCall(["subuser","install",programName])
  else:
    exit()

def getImageTagOfProgram(programName, imageTAG='latest'):
  """ Return the Repository Name of a program or None, if there is no installed image for that program. """
  repoName = None
  dockerImageMatrix = getParsedDockerImages(noTrunc=True)
  if getUniqueRowByRepTag(dockerImageMatrix, 'subuser-'+programName, imageTAG):
    repoName = 'subuser-'+programName
  return repoName

def getImageTagOfInstalledProgram(programName):
  """ Return the tag of the docker image of an installed program.
If that program is not yet installed, install it.
  """
  imageTag = getImageTagOfProgram(programName)
  if imageTag == None:
    askToInstallProgram(programName)
    imageTag = "subuser-"+programName

  return imageTag

def isProgramsImageInstalled(programName):
  """ Return True if the programs image tag is installed.  False otherwise. """
  return not (getImageTagOfProgram(programName) == None)

def inspectImage(imageTag):
  """ Returns a dictionary coresponding to the json outputed by docker inspect. """
  dockerInspectOutput = subprocess.check_output(["docker","inspect",imageTag])
  imageInfo = json.loads(dockerInspectOutput)
  return imageInfo[0]

def getImageID(imageTag):
  """ Returns the ID(as a string) of an image given that image's tag. """
  return inspectImage(imageTag)["id"]

def getRunningProgramsWithNames(names):
  """ Returns a very crude listing from docker ps. Not a real list of the names of running programs or anything. """
  psOutput = subprocess.check_output(["docker","ps"])
  psOutput = psOutput.split("\n")
  psOutput = psOutput[1:]
  def amongProgramsToBeWaitedOn(psOutputLine):
    tags = ["subuser-"+name for name in names]
    if psOutputLine == '': return False
    outputLineWords = psOutputLine.split()
    tagName = outputLineWords[1].split(':')[0]
    return tagName in tags
  return [psOutputLine for psOutputLine in psOutput if amongProgramsToBeWaitedOn(psOutputLine) ]

def isProgramRunning(name):
  """ Returns True if the program is currently running. """
  return len(getRunningProgramsWithNames([name])) > 0

def areProgramsRunning(programs):
  """ Returns True if at least one of the listed programs is currently running. """
  return len(getRunningProgramsWithNames(programs)) > 0


def getParsedDockerImages(noTrunc=False):
  """ Parse `docker images` related output for easier access: return a dictionary of Columns Lists
  no-trunc: if False: truncate output 
  """
  dockerImageMatrix = {'REPOSITORY' : [], 'TAG' : [], 'ID' : [], 'CREATED' : [], 'SIZE' : []}
  if noTrunc:
    roughImagesList = subprocess.check_output(["docker","images", "--no-trunc=true"])
  else:
    roughImagesList = subprocess.check_output(["docker","images", "--no-trunc=false"])

  #solve the problem with white space allowed in RepoNames and Tags
  #Columns: REPOSITORY   TAG   IMAGE ID   CREATED   VIRTUAL SIZE
  splitPoints = {'REPOSITORY' : -1, 'TAG' : -1, 'IMAGE ID' : -1, 'CREATED' : -1, 'VIRTUAL SIZE' : -1}
  imagesLinesList = [line for line in roughImagesList.split("\n") if line.strip()]
  topRowNames = imagesLinesList[0]

  for name in splitPoints.keys():
    splitPoints[name] = topRowNames.find(name)
    if splitPoints[name] == -1:
      sys.exit("ERROR: could not parse 'docker images' output")
      
  for line in imagesLinesList[1:]:
    dockerImageMatrix['REPOSITORY'].append(line[splitPoints['REPOSITORY']:splitPoints['TAG']].strip())
    dockerImageMatrix['TAG'].append(line[splitPoints['TAG']:splitPoints['IMAGE ID']].strip())
    dockerImageMatrix['ID'].append(line[splitPoints['IMAGE ID']:splitPoints['CREATED']].strip())
    dockerImageMatrix['CREATED'].append(line[splitPoints['CREATED']:splitPoints['VIRTUAL SIZE']].strip())
    dockerImageMatrix['SIZE'].append(line[splitPoints['VIRTUAL SIZE']:len(line)].strip())
  return dockerImageMatrix
  
def getAllRepoNameWhichStartWith(dockerImageMatrix, repoNamePrefix='subuser-'):
  """Returns a list of REPOSITORY names starting with repoNamePrefix
  Arguments see: getParsedDockerImages()
  e.g.
  dockerImageMatrix = getParsedDockerImages(noTrunc=True)
  print(getAllRepoNameWhichStartWith(dockerImageMatrix))
  """
  return [name for name in dockerImageMatrix['REPOSITORY'] if name.startswith(repoNamePrefix)]
  
def getUniqueRowByRepTag(dockerImageMatrix, searchRepoName, searchTag='latest'):
  """Returns a dictionary of columns (line row): repoName, tag
  if not found: empty dictionary
  e.g.
  dockerImageMatrix = getParsedDockerImages(noTrunc=True)
  print(getUniqueRowByRepTag(dockerImageMatrix, 'subuser-vim', 'latest'))
  
  e.g. get ID
  print(getUniqueRowByRepTag(dockerImageMatrix, 'subuser-vim', 'latest')['ID])
  
  e.g. get SIZE
  print(getUniqueRowByRepTag(dockerImageMatrix, 'subuser-vim', 'latest')['SIZE])
  
  e.g. check for existence
  if getUniqueRowByRepTag(dockerImageMatrix, 'subuser-vim', 'latest'):
    print("Found: 'subuser-vim', 'latest)
  else:
    print("Could NOT Find: 'subuser-vim', 'latest)
  """
  dockerImageMatrixRow = {}
  for index, (repoName, tag) in enumerate(zip(dockerImageMatrix['REPOSITORY'], dockerImageMatrix['TAG'])):
    if repoName == searchRepoName and tag == searchTag:
      #PS: I split this on purpose instead of a long line: can also be put on one line if you want
      dockerImageMatrixRow = {'REPOSITORY' : dockerImageMatrix['REPOSITORY'][index], 
                              'TAG' : dockerImageMatrix['TAG'][index],
                              'ID' : dockerImageMatrix['ID'][index], 
                              'CREATED' : dockerImageMatrix['CREATED'][index],
                              'SIZE' : dockerImageMatrix['SIZE'][index]}
      #Repo/Tag combinations are supposed to be unique
      break
  return dockerImageMatrixRow
  
def getSubuserDockerRepoNameTagsText(addNewLine=False, indentSpaces=0):
  """ Returns a string representing a sorted list of subuser-program names which are actual docker images
  Arguments:
   - indentSpaces: can be set for nicer output especially togehter with: addNewLine
   - addNewLine: if True each installed program's name starts at a new line
  
  e.g.: `print(getInstalledProgramsText(addNewLine=True, indentSpaces=3))`
  """
  outText = ''
  indentionString = ''
  if indentSpaces > 0:
    indentionString = ' ' * indentSpaces
    
  dockerSubuserProgramsRepoTagList = []
  dockerImageMatrix = getParsedDockerImages(noTrunc=True)
  for index, name in enumerate(dockerImageMatrix['REPOSITORY']):
    if name.startswith('subuser-'):
      dockerSubuserProgramsRepoTagList.append('%s:%s' % (dockerImageMatrix['REPOSITORY'][index], dockerImageMatrix['TAG'][index]))
    
  if addNewLine:
    for program in sorted(dockerSubuserProgramsRepoTagList):
      outText = ''.join([outText, indentionString, program, '\n'])
  else:
    outText = indentionString + ' '.join(sorted(dockerSubuserProgramsRepoTagList))
  return outText
  
