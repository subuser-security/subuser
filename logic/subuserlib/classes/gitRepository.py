# -* coding: utf-8 -*-

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

gitExecutable = None

class GitRepository(UserOwnedObject):
  def __init__(self,user,path):
    UserOwnedObject.__init__(self,user)
    self.path = path
    self.__gitExecutable = None

  def getGitExecutable(self):
    global gitExecutable
    if gitExecutable is None:
      gitExecutable = [subuserlib.executablePath.which("git",excludeDir=self.user.config["bin-dir"])]
      if gitExecutable is None:
        sys.exit("Git is not installed. Subuser requires git to run.")
    return gitExecutable

  def assertGitSetup(self):
    self.getGitExecutable()
    def getConfig(key):
      (returncode,stdout,stderr) = self.user.endUser.callCollectOutput(gitExecutable + ["config","--get",key])
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

  def clone(self,origin):
    """
    Clone an external repository in order to create this repository.
    """
    return self.user.endUser.call(self.getGitExecutable()+["clone", origin, self.path])

  def run(self,args):
    returncode,_ = self.__run(args)
    return returncode

  def runCollectOutput(self,args,eatStderr=False):
    return self.__run(args,eatStderr=eatStderr)

  def __run(self,args,eatStderr=False):
    """
    Run git with the given command line arguments and return a tuple with (returncode,output).
    """
    try:
      gitArgs = self.getGitExecutable()+args
      (returncode,stdout,stderr) = self.user.endUser.callCollectOutput(gitArgs,cwd=self.path)
      if ((not eatStderr) and stderr.strip()) or returncode != 0:
        self.user.registry.log(self.path+": "+" ".join(gitArgs),verbosityLevel=2)
        self.user.registry.log(stdout,verbosityLevel=2)
        self.user.registry.log(stderr,verbosityLevel=2)
      else:
        self.user.registry.log(self.path+": "+" ".join(gitArgs),verbosityLevel=5)
        self.user.registry.log(stdout,verbosityLevel=5)
        self.user.registry.log(stderr,verbosityLevel=5)
      if stderr and not eatStderr:
        raise GitException(stderr)
      return (returncode,stdout)
    except OSError as e:
      if e.errno == errno.EEXIST:
        sys.exit("You must have git installed to use subuser.")
      else:
        raise e

  def runShowOutput(self,args):
    self.user.endUser.call(self.getGitExecutable()+args,cwd=self.path)

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
      raise OSError("Running git in "+self.path+" with args "+str(command)+" failed.")
    return output.strip()

  def doesHaveUncommittedChanges(self,ref):
    command = ["diff-index","--name-only",ref]
    (returncode,output) = self.runCollectOutput(command)
    if returncode != 0:
      # Just ignore it if command failed
      return False
    if output:
      return True
    else:
      return False

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
    self.gitRepository = gitRepository
    self.commit = commit
    self.__lsTreeCache = {}

  def lsTree(self):
    """
    Returns a list of tuples of the form:
    (mode,type,hash,path)

    Coresponding to the items found in the subfolder.
    """
    args = [self.commit,"-rtl"]
    argsTuple = tuple(args)
    try:
      return self.__lsTreeCache[argsTuple]
    except KeyError:
      pass
    (returncode,output) = self.gitRepository.runCollectOutput(["ls-tree"]+args)
    if returncode != 0:
      return [] # It is simpler to just return [] here than to check if the repository is properly initialized everywhere else.
    lines = output.splitlines()
    items = []
    for line in lines:
      mode,objectType,objectHash,size,path = line.split(maxsplit=4)
      line = {"mode":mode,"type":objectType,"hash":objectHash,"size":size,"path":path}
      items.append(line)
    self.__lsTreeCache[argsTuple] = items
    return items

  def _ls(self, subfolder,objectType=None):
    """
    Returns a list of file and folder names.

    >>> from subuserlib.classes.gitRepository import GitRepository
    >>> gitRepository = GitRepository(subuserlib.classes.gitRepository.getUser(),subuserlib.classes.gitRepository.hashtestDir)
    >>> fileStructure = gitRepository.getFileStructureAtCommit("master")
    >>> print(",".join(fileStructure.ls("./")))
    bar,blah
    """
    if subfolder == "./" or subfolder == "/":
      subfolder = ""
    items = self.lsTree()
    names = []
    for item in items:
      folder,name = os.path.split(item["path"])
      if os.path.normpath(folder) == os.path.normpath(subfolder):
        if objectType is None or objectType == item["type"]:
          names.append(name)
    return names

  def _lsFiles(self,subfolder):
    """
    Returns a list of paths to files in the subfolder.
    Paths are relative to the repository as a whole.

    >>> from subuserlib.classes.gitRepository import GitRepository
    >>> gitRepository = GitRepository(subuserlib.classes.gitRepository.getUser(),subuserlib.classes.gitRepository.hashtestDir)
    >>> fileStructure = gitRepository.getFileStructureAtCommit("master")
    >>> print(",".join(fileStructure.lsFiles("./")))
    blah
    """
    return self.ls(subfolder,"blob")

  def _lsFolders(self,subfolder):
    """
    Returns a list of paths to folders in the subfolder.
    Paths are relative to the repository as a whole.

    >>> from subuserlib.classes.gitRepository import GitRepository
    >>> gitRepository = GitRepository(subuserlib.classes.gitRepository.getUser(),subuserlib.classes.gitRepository.hashtestDir)
    >>> fileStructure = gitRepository.getFileStructureAtCommit("master")
    >>> print(",".join(fileStructure.lsFolders("./")))
    bar
    """
    return self.ls(subfolder,"tree")

  def _exists(self,path):
    """
    >>> from subuserlib.classes.gitRepository import GitRepository
    >>> gitRepository = GitRepository(subuserlib.classes.gitRepository.getUser(),subuserlib.classes.gitRepository.hashtestDir)
    >>> fileStructure = gitRepository.getFileStructureAtCommit("master")
    >>> fileStructure.exists("./blah")
    True
    >>> fileStructure.exists("./non-existant")
    False
    """
    (dir,filename) = os.path.split(path)
    for object in self.lsTree():
      (_,existing_filename) = os.path.split(object["path"])
      if filename == existing_filename:
        return True
    return False

  def _read(self,path):
    """
    Returns the contents of the given file at the given commit.

    >>> from subuserlib.classes.gitRepository import GitRepository
    >>> gitRepository = GitRepository(subuserlib.classes.gitRepository.getUser(),subuserlib.classes.gitRepository.hashtestDir)
    >>> fileStructure = gitRepository.getFileStructureAtCommit("master")
    >>> print(fileStructure.read("./blah"))
    blahblah
    <BLANKLINE>
    """
    (errorcode,content) = self.gitRepository.runCollectOutput(["show",self.commit+":"+path],eatStderr=True)
    if errorcode != 0:
      raise OSError("Git show exited with error "+str(errorcode)+". File does not exist.\nRepo:"+self.gitRepository.path+"\nPath: "+path+"\nCommit: "+self.commit+"\n")
    return content

  def _readBinary(self,path):
    return self.read(path).encode()

  def _getMode(self,path):
    """
    >>> from subuserlib.classes.gitRepository import GitRepository
    >>> gitRepository = GitRepository(subuserlib.classes.gitRepository.getUser(),subuserlib.classes.gitRepository.hashtestDir)
    >>> fileStructure = gitRepository.getFileStructureAtCommit("master")
    >>> print(fileStructure.getModeString("./blah"))
    100644
    """
    allObjects = self.lsTree()
    for treeObject in allObjects:
      if os.path.normpath(treeObject["path"]) == os.path.normpath(path):
        return int(treeObject["mode"],8)

  def _getSize(self,path):
    """
    >>> from subuserlib.classes.gitRepository import GitRepository
    >>> gitRepository = GitRepository(subuserlib.classes.gitRepository.getUser(),subuserlib.classes.gitRepository.hashtestDir)
    >>> fileStructure = gitRepository.getFileStructureAtCommit("master")
    >>> print(fileStructure.getSize("./blah"))
    9
    """
    allObjects = self.lsTree()
    for treeObject in allObjects:
      if os.path.normpath(treeObject["path"]) == os.path.normpath(path):
        return int(treeObject["size"],10)

  def isLegalSymlink(self,path):
    """
    There shouldn't be any risk involved with symlinks in git,
    since git already reads only files which have been checked in.
    """
    return True

class GitException(Exception):
  pass
