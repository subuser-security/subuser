# -*- coding: utf-8 -*-

"""
This is a Class which allows one to manipulate a git repository.
"""

#external imports
import os
import tempfile
import sys
import errno
#internal imports
from subuserlib.classes.userOwnedObject import UserOwnedObject
from subuserlib.classes.fileStructure import FileStructure
import subuserlib.executablePath
import subuserlib.test
if subuserlib.test.testing:
  hashtestDir = subuserlib.test.hashtestDir
  def getUser():
    return subuserlib.test.getUser()

class GitRepository(UserOwnedObject):
  def __init__(self,user,path):
    UserOwnedObject.__init__(self,user)
    self.__path = path
    self.__gitExecutable = None

  def getPath(self):
    return self.__path

  def getGitExecutable(self):
    if self.__gitExecutable is None:
      self.__gitExecutable = [subuserlib.executablePath.which("git",excludeDir=self.getUser().getConfig()["bin-dir"])]
      if self.__gitExecutable is None:
        sys.exit("Git is not installed. Subuser requires git to run.")
      def getConfig(key):
        (returncode,stdout,stderr) = self.getUser().getEndUser().callCollectOutput(self.__gitExecutable + ["config","--get",key])
        if returncode == 0:
          return stdout
        else:
          return None
      if getConfig("user.name") is None or getConfig("user.email") is None:
        sys.exit("""You must configure git's user.name and user.email options before using subuser.
Do so by running
$ git config --global user.name "John Doe"
$ git config --global user.email johndoe@example.com
""")
    return self.__gitExecutable

  def clone(self,origin):
    """
    Clone an external repository in order to create this repository.
    """
    return self.getUser().getEndUser().call(self.getGitExecutable()+["clone", origin, self.getPath()])

  def run(self,args):
    """
    Run git with the given command line arguments.
    """
    try:
      gitArgs = self.getGitExecutable()+args
      (returncode,stdout,stderr) = self.getUser().getEndUser().callCollectOutput(gitArgs,cwd=self.getPath())
      self.getUser().getRegistry().log(self.getPath()+": "+" ".join(gitArgs),verbosityLevel=3)
      self.getUser().getRegistry().log(stdout,verbosityLevel=3)
      self.getUser().getRegistry().log(stderr,verbosityLevel=3)
      if stderr:
        raise GitException(stderr)
      return returncode
    except OSError as e:
      if e.errno == errno.EEXIST:
        sys.exit("You must have git installed to use subuser.")
      else:
        raise e

  def runShowOutput(self,args):
    self.getUser().getEndUser().call(self.getGitExecutable()+args,cwd=self.getPath())

  def runCollectOutput(self,args,eatStderr=False):
    """
    Run git with the given command line arguments and return a tuple with (returncode,output).
    """
    try:
      gitArgs = self.getGitExecutable()+args
      (returncode,stdout,stderr) = self.getUser().getEndUser().callCollectOutput(gitArgs,cwd=self.getPath())
      self.getUser().getRegistry().log(self.getPath()+": "+" ".join(gitArgs),verbosityLevel=3)
      self.getUser().getRegistry().log(stderr,verbosityLevel=3)
      if stderr and not eatStderr:
        raise GitException(stderr)
      return (returncode,stdout)
    except OSError as e:
      if e.errno == errno.EEXIST:
        sys.exit("You must have git installed to use subuser.")
      else:
        raise e

  def doesCommitExist(self,commit):
    """
    Return true if the commit or reference exists.
    """
    try:
      (returncode,stdout) = self.runCollectOutput(["cat-file","-t",commit])
    except GitException:
      return False
    if returncode == 0 and "commit" in stdout:
      return True
    else:
      return False

  def getFileStructureAtCommit(self,commit):
    """
    Get a ``FileStructure`` object which relates to the given git commit.
    """
    return GitFileStructure(self,commit)

  def commit(self,message):
    """
    Run git commit with the given commit message.
    """
    return self.run(["commit","--message",message])

  def checkout(self,commit,files=[]):
    """
    Run git checkout
    """
    self.run(["checkout",commit]+files)

  def getHashOfRef(self,ref):
    command = ["show-ref","-s",ref]
    (returncode,output) = self.runCollectOutput(command)
    if returncode != 0:
      raise OSError("Running git in "+self.getPath()+" with args "+str(command)+" failed.")
    return output.strip()

class GitFileStructure(FileStructure):
  def __init__(self,gitRepository,commit):
    """
    Initialize the file structure.

    Here we setup test stuff:
    >>> import subuserlib.subprocessExtras
    >>> import subuserlib.classes.gitRepository
    >>> subuserlib.subprocessExtras.call(["git","init"],cwd=subuserlib.classes.gitRepository.hashtestDir)
    0
    >>> subuserlib.subprocessExtras.call(["git","add","."],cwd=subuserlib.classes.gitRepository.hashtestDir)
    0
    >>> subuserlib.subprocessExtras.call(["git","commit","-m","Initial commit"],cwd=subuserlib.classes.gitRepository.hashtestDir)
    0
    """
    self.__gitRepository = gitRepository
    self.__commit = commit
    self.__lsTreeCache = {}

  def getCommit(self):
    return self.__commit

  def getRepository(self):
    return self.__gitRepository

  def lsTree(self, subfolder, extraArgs=[]):
    """
    Returns a list of tuples of the form:
    (mode,type,hash,path)

    Coresponding to the items found in the subfolder.
    """
    if not subfolder.endswith("/"):
      subfolder += "/"
    if subfolder == "/":
      subfolder = "./"
    args = extraArgs+[self.getCommit(),subfolder]
    argsTuple = tuple(args)
    try:
      return self.__lsTreeCache[argsTuple]
    except KeyError:
      pass
    (returncode,output) = self.getRepository().runCollectOutput(["ls-tree"]+args)
    if returncode != 0:
      return [] # This commenting out is intentional. It is simpler to just return [] here than to check if the repository is properly initialized everywhere else.
    lines = output.splitlines()
    items = []
    for line in lines:
      mode,objectType,rest = line.split(" ",2)
      objectHash,path = rest.split("\t",1)
      items.append((mode,objectType,objectHash,path))
    self.__lsTreeCache[argsTuple] = items
    return items

  def ls(self, subfolder, extraArgs=[]):
    """
    Returns a list of file and folder paths.
    Paths are relative to the repository as a whole.

    >>> from subuserlib.classes.gitRepository import GitRepository
    >>> gitRepository = GitRepository(subuserlib.classes.gitRepository.getUser(),subuserlib.classes.gitRepository.hashtestDir)
    >>> fileStructure = gitRepository.getFileStructureAtCommit("master")
    >>> print(",".join(fileStructure.ls("./")))
    bar,blah
    """
    items = self.lsTree(subfolder,extraArgs)
    paths = []
    for item in items:
      paths.append(item[3])
    return paths

  def lsFiles(self,subfolder):
    """
    Returns a list of paths to files in the subfolder.
    Paths are relative to the repository as a whole.

    >>> from subuserlib.classes.gitRepository import GitRepository
    >>> gitRepository = GitRepository(subuserlib.classes.gitRepository.getUser(),subuserlib.classes.gitRepository.hashtestDir)
    >>> fileStructure = gitRepository.getFileStructureAtCommit("master")
    >>> print(",".join(fileStructure.lsFiles("./")))
    blah
    """
    return list(set(self.ls(subfolder)) - set(self.lsFolders(subfolder)))

  def lsFolders(self,subfolder):
    """
    Returns a list of paths to folders in the subfolder.
    Paths are relative to the repository as a whole.

    >>> from subuserlib.classes.gitRepository import GitRepository
    >>> gitRepository = GitRepository(subuserlib.classes.gitRepository.getUser(),subuserlib.classes.gitRepository.hashtestDir)
    >>> fileStructure = gitRepository.getFileStructureAtCommit("master")
    >>> print(",".join(fileStructure.lsFolders("./")))
    bar
    """
    return self.ls(subfolder,extraArgs=["-d"])

  def exists(self,path):
    """
    >>> from subuserlib.classes.gitRepository import GitRepository
    >>> gitRepository = GitRepository(subuserlib.classes.gitRepository.getUser(),subuserlib.classes.gitRepository.hashtestDir)
    >>> fileStructure = gitRepository.getFileStructureAtCommit("master")
    >>> fileStructure.exists("./blah")
    True
    >>> fileStructure.exists("./non-existant")
    False
    """
    try:
      self.read(path)
      return True
    except OSError:
      return False

  def read(self,path):
    """
    Returns the contents of the given file at the given commit.

    >>> from subuserlib.classes.gitRepository import GitRepository
    >>> gitRepository = GitRepository(subuserlib.classes.gitRepository.getUser(),subuserlib.classes.gitRepository.hashtestDir)
    >>> fileStructure = gitRepository.getFileStructureAtCommit("master")
    >>> print(fileStructure.read("./blah"))
    blahblah
    <BLANKLINE>
    """
    (errorcode,content) = self.getRepository().runCollectOutput(["show",self.getCommit()+":"+path],eatStderr=True)
    if errorcode != 0:
      raise OSError("Git show exited with error "+str(errorcode)+". File does not exist.\nPath: "+path+"\nCommit: "+self.getCommit()+"\n")
    return content

  def readBinary(self,path):
    return self.read(path).encode()

  def getMode(self,path):
    """
    >>> from subuserlib.classes.gitRepository import GitRepository
    >>> gitRepository = GitRepository(subuserlib.classes.gitRepository.getUser(),subuserlib.classes.gitRepository.hashtestDir)
    >>> fileStructure = gitRepository.getFileStructureAtCommit("master")
    >>> print(fileStructure.getModeString("./blah"))
    100644
    """
    allObjects = self.lsTree("./",extraArgs=["-r"])
    for treeObject in allObjects:
      if os.path.normpath(treeObject[3]) == os.path.normpath(path):
        return int(treeObject[0],8)

class GitException(Exception):
  pass
