#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
The DockerDaemon object allows us to communicate with the Docker daemon via the Docker HTTP REST API.
"""

#external imports
import urllib,tarfile,os,tempfile,fnmatch,re,json,io,sys
try:
 import httplib
except ImportError:
 import http.client
 httplib = http.client
#internal imports
import subuserlib.subprocessExtras,subuserlib.classes.userOwnedObject,subuserlib.classes.uhttpConnection,subuserlib.docker,subuserlib.test,subuserlib.classes.mockDockerDaemon

def archiveBuildContext(archive,directoryWithDockerfile,excludePatterns,dockerfile=None):
  """
  Archive files from directoryWithDockerfile into the FileObject archive excluding files who's paths(relative to directoryWithDockerfile) are in excludePatterns.
  If dockerfile is set to a string, include that string as the file Dockerfile in the archive.
  """
  # Inspired by and partialy taken from https://github.com/docker/docker-py
  contexttarfile = tarfile.open(mode="w",fileobj=archive)
  if directoryWithDockerfile:
    fileList = os.walk(directoryWithDockerfile)
  else:
    fileList = []
  for dirpath, _, filenames in fileList:
    relpath = os.path.relpath(dirpath, directoryWithDockerfile)
    if relpath == '.':
      relpath = ''
    for filename in filenames:
      exclude = False
      fileNameInArchive = os.path.join(relpath,filename)
      for excludePattern in excludePatterns:
        if fnmatch.fnmatch(fileNameInArchive,excludePattern):
          exclude = True
      if not exclude:
        contexttarfile.add(os.path.join(directoryWithDockerfile,fileNameInArchive), arcname=fileNameInArchive,recursive=False) # Explicit setting of recursive is not strictly necessary.
  # Add the provided Dockerfile if necessary
  if not dockerfile == None:
    dockerfileFileObject = io.StringIO(dockerfile)
    tarinfo = tarfile.TarInfo(name="Dockerfile")
    dockerfileFileObject.seek(0, os.SEEK_END) # TODO either I am doing this wrong, or python3 sucks.
    tarinfo.size = dockerfileFileObject.tell()
    dockerfileFileObject.seek(0)
    contexttarfile.addfile(tarinfo,dockerfileFileObject)
  contexttarfile.close()
  archive.seek(0)

def readAndPrintSreamingBuildStatus(response):
  # Warning, reading from an httpresponse is not exactly high level programming ;)
  output = ""
  chunk = None
  while chunk == None or not chunk == "":
    chunk = response.read(80)
    if "\n" in chunk:
      try:
        lineStart = output.rindex("\n")
      except ValueError:
        lineStart = 0
      lineContainingRegion = output[lineStart:] + chunk[:chunk.rindex("\n")]
      for line in lineContainingRegion.split("\n"):
        if line:
          lineJson = json.loads(line)
          try:
              if "stream" in lineJson:
                sys.stdout.write(lineJson["stream"])
              else:
                print(lineJson["errorDetail"]["message"])
                print(lineJson["error"])
          except (KeyError,ValueError): # TODO, handle errorDetail messages
            sys.stdout.write(line)
    output += chunk
  return output

class DockerDaemon(subuserlib.classes.userOwnedObject.UserOwnedObject):
  __connection = None

  def __init__(self,user):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)

  def getConnection(self):
    """
     Get an `HTTPConnection <https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection>`_ to the Docker daemon.

     Note: You can find more info in the `Docker API docs <https://docs.docker.com/reference/api/docker_remote_api_v1.13/>`_
    """
    if not self.__connection:
      subuserlib.docker.getAndVerifyDockerExecutable()
      self.__connection = subuserlib.classes.uhttpConnection.UHTTPConnection("/var/run/docker.sock")
    return self.__connection

  def getImageProperties(self,imageTagOrId):
    """
     Returns a dictionary of image properties, or None if the image does not exist.
    """
    self.getConnection().request("GET","/images/"+imageTagOrId+"/json")
    response = self.getConnection().getresponse()
    if not response.status == 200:
      response.read() # Read the response and discard it to prevent the server from getting locked up: http://stackoverflow.com/questions/3231543/python-httplib-responsenotready
      return None
    else:
      return json.loads(response.read())

  def removeImage(self,imageId):
    self.getConnection().request("DELETE","/images/"+imageId)
    response = self.getConnection().getresponse()
    if not response.status == 200:
      raise ImageDoesNotExistsException("The image "+imageId+" could not be deleted.\n"+response.read())
    else:
      response.read()

  def build(self,directoryWithDockerfile=None,useCache=True,rm=False,forceRm=False,quiet=False,tag=None,dockerfile=None,quietClient=False):
    """
    Build a Docker image.  If a the dockerfile argument is set to a string, use that string as the Dockerfile.  Returns the newly created images Id or raises an exception if the build fails.

    Most of the options are passed directly on to Docker.

    The quietClient option makes it so that this function does not print any of Docker's status messages when building.
    """
    # Inspired by and partialy taken from https://github.com/docker/docker-py
    queryParameters =  {
      't': tag,
      'q': quiet,
      'nocache': not useCache,
      'rm': rm,
      'forcerm': forceRm
      }
    queryParametersString = urllib.urlencode(queryParameters)
    excludePatterns = []
    if directoryWithDockerfile:
      dockerignore = os.path.join(directoryWithDockerfile, '.dockerignore')
      if os.path.exists(dockerignore):
        with open(dockerignore, 'r') as f:
          exclude = list(filter(bool, f.read().split('\n')))
    with tempfile.TemporaryFile() as tmpArchive:
      archiveBuildContext(tmpArchive,directoryWithDockerfile,excludePatterns,dockerfile=dockerfile)
      self.getConnection().request("POST","/build?"+queryParametersString,body=tmpArchive)
      try:
        response = self.getConnection().getresponse()
      except httplib.ResponseNotReady as rnr:
        raise ImageBuildException(rnr)

    if response.status != 200:
      if quietClient:
        response.read()
      else:
        readAndPrintSreamingBuildStatus(response)
      raise ImageBuildException("Building image failed.\n"
                     +"status: "+str(response.status)+"\n"
                     +"Reason: "+response.reason+"\n")

    if quietClient:
      output = response.read()
    else:
      output = readAndPrintSreamingBuildStatus(response)
    # Now we move to regex code stolen from the official python Docker bindings.
    search = r'Successfully built ([0-9a-f]+)'
    match = re.search(search, output)
    if not match:
      raise ImageBuildException("Unexpected server response when building image.")
    shortId = match.group(1) #This is REALLY ugly!
    return self.getImageProperties(shortId)["Id"]

  def execute(self,args,cwd=None):
    subuserlib.docker.runDockerAndExitIfItFails(args,cwd=cwd)

class ImageBuildException(Exception):
  pass

class ImageDoesNotExistsException(Exception):
  pass

if subuserlib.test.testing:
  DockerDaemon = subuserlib.classes.mockDockerDaemon.MockDockerDaemon

