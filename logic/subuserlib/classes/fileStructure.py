# -*- coding: utf-8 -*-
# pylint: disable=no-init,old-style-class

"""
A file structure object is a read only view of a file structure, such as a real directory or a git tree.
"""

#external imports
import abc
import hashlib
import os
import stat
import sys
#internal imports
import subuserlib.test
if subuserlib.test.testing:
  hashtestDir = subuserlib.test.hashtestDir

class FileStructure():
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def ls(self, subfolder):
    """
    Returns a list of file and folder paths.
    Paths are relative to the root of the FileStructure.
    """
    pass

  @abc.abstractmethod
  def lsFiles(self,subfolder):
    """
    Returns a list of paths to files in the subfolder.
    Paths are relative to the root of the FileStructure.
    """
    pass

  @abc.abstractmethod
  def lsFolders(self,subfolder):
    """
    Returns a list of paths to folders in the subfolder.
    Paths are relative to the root of the FileStructure.
    """
    pass

  @abc.abstractmethod
  def exists(self,path):
    pass

  @abc.abstractmethod
  def read(self,path):
    """
    Returns the contents of the given file.
    """
    pass

  @abc.abstractmethod
  def readBinary(self,path):
    """
    Returns the contents of the given file.
    """
    pass

  @abc.abstractmethod
  def getMode(self,path):
    pass

  def getModeString(self,path):
    """
    Return the human readable mode string for the mode in octal notation.
    """
    octalMode = oct(self.getMode(path))
    if sys.version_info[0] == 2:
      octalMode = octalMode[1:]
    if sys.version_info[0] == 3:
      octalMode = octalMode[2:]
    return octalMode

  def hash(self,path):
    """
    Return the SHA1 hash of the file or directory.

    In the case of directectories, hashes alphabetically and hashes subdirectories first.

    Hashes the following:
      - Relative file path
      - File mode
      - File contents

    Return the hash as a hexidecimal string.

    >>> from subuserlib.classes.fileStructure import FileStructure
    >>> fileStructure = BasicFileStructure(subuserlib.classes.fileStructure.hashtestDir)
    >>> fileStructure.hash("./")
    '6b9c28475016167ba6b58ad37ea9eb56d7364cb9'
    """
    SHAhash = hashlib.sha1()
    # TODO - what about symlinks?
    # TODO - what about devices?
    # TODO - what about hard link loops?
    # TODO - what about sockets?
    # TODO - what about named pipes?
    def hashFile(path):
      encodedPath = path.encode("utf-8","replace")
      SHAhash.update(encodedPath)
      SHAhash.update(self.getModeString(path).encode("utf-8"))
      SHAhash.update(self.readBinary(path))
    def hashDir(path):
      # Hash subdirectories
      subdirs = self.lsFolders(path)
      subdirs.sort()
      for subdir in subdirs:
        hashDir(subdir)
      # Hash files
      files = self.lsFiles(path)
      files.sort()
      for fileToHash in files:
        hashFile(fileToHash)
    hashDir(path)
    return SHAhash.hexdigest()

class BasicFileStructure(FileStructure):
  """
  A FileStructure backed by real files.
  """
  def __init__(self,path):
    self.__path = path

  def getPath(self):
    return self.__path

  def getPathInStructure(self,path):
    """
    Given a relative path within the file structure, return an absolute path.
    """
    return os.path.join(self.getPath(),path)

  def ls(self, subfolder):
    """
    >>> from subuserlib.classes.fileStructure import FileStructure
    >>> fileStructure = BasicFileStructure(subuserlib.classes.fileStructure.hashtestDir)
    >>> print(",".join(fileStructure.ls("./")))
    bar,blah
    """
    paths = []
    path = self.getPathInStructure(subfolder)
    for path in os.listdir(path):
      paths.append(os.path.normpath(os.path.join(subfolder,path)))
    paths.sort()
    return paths

  def lsFiles(self,subfolder):
    """
    >>> from subuserlib.classes.fileStructure import FileStructure
    >>> import os
    >>> fileStructure = BasicFileStructure(subuserlib.classes.fileStructure.hashtestDir)
    >>> print(",".join(fileStructure.lsFiles("./")))
    blah
    """
    files = []
    for path in self.ls(subfolder):
      if os.path.isfile(self.getPathInStructure(path)):
        files.append(os.path.normpath(path))
    return files

  def lsFolders(self,subfolder):
    """
    >>> from subuserlib.classes.fileStructure import FileStructure
    >>> import os
    >>> fileStructure = BasicFileStructure(subuserlib.classes.fileStructure.hashtestDir)
    >>> print(",".join(fileStructure.lsFolders("./")))
    bar
    """
    folders = []
    for path in self.ls(subfolder):
      pathInStructure = self.getPathInStructure(path)
      if os.path.isdir(pathInStructure):
        folders.append(os.path.normpath(path))
    return folders

  def exists(self,path):
    """
    >>> from subuserlib.classes.fileStructure import FileStructure
    >>> import os
    >>> fileStructure = BasicFileStructure(subuserlib.classes.fileStructure.hashtestDir)
    >>> fileStructure.exists("./blah")
    True
    >>> fileStructure.exists("./non-existant")
    False
    """
    return os.path.exists(self.getPathInStructure(path))

  def read(self,path):
    """
    >>> from subuserlib.classes.fileStructure import BasicFileStructure
    >>> import os
    >>> fileStructure = BasicFileStructure(subuserlib.classes.fileStructure.hashtestDir)
    >>> print(fileStructure.read("./blah"))
    blahblah
    <BLANKLINE>
    """
    with open(self.getPathInStructure(path),"r",encoding="utf-8") as fd:
      return fd.read()

  def readBinary(self,path):
    """
    >>> from subuserlib.classes.fileStructure import FileStructure
    >>> import os
    >>> fileStructure = BasicFileStructure(subuserlib.classes.fileStructure.hashtestDir)
    >>> print(fileStructure.read("./blah"))
    blahblah
    <BLANKLINE>
    """
    with open(self.getPathInStructure(path),"rb") as fd:
      return fd.read()

  def getMode(self,path):
    """
    >>> from subuserlib.classes.fileStructure import FileStructure
    >>> import os
    >>> fileStructure = BasicFileStructure(subuserlib.classes.fileStructure.hashtestDir)
    >>> print(fileStructure.getModeString("./blah"))
    100664
    """
    return os.stat(self.getPathInStructure(path))[stat.ST_MODE]
