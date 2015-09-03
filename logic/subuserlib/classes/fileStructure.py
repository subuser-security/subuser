#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.
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
#import ...

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
    >>> fileStructure = BasicFileStructure("/home/travis/hashtest")
    >>> fileStructure.hash("./")
    'c5c5368bf02e0105e98eca5f07eef6bb2907188e'
    """
    SHAhash = hashlib.sha1()
    # TODO - what about symlinks?
    # TODO - what about devices?
    # TODO - what about hard link loops?
    # TODO - what about sockets?
    # TODO - what about named pipes?
    def hashFile(path):
      SHAhash.update(path.encode("utf-8"))
      SHAhash.update(self.getModeString(path).encode("utf-8"))
      SHAhash.update(self.read(path).encode("utf-8"))
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
    >>> fileStructure = BasicFileStructure("/home/travis/hashtest")
    >>> print(",".join(fileStructure.ls("./")))
    bar,blah
    """
    paths = []
    for path in os.listdir(self.getPathInStructure(subfolder)):
      paths.append(os.path.normpath(os.path.join(subfolder,path)))
    paths.sort()
    return paths

  def lsFiles(self,subfolder):
    """
    >>> from subuserlib.classes.fileStructure import FileStructure
    >>> fileStructure = BasicFileStructure("/home/travis/hashtest")
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
    >>> fileStructure = BasicFileStructure("/home/travis/hashtest")
    >>> print(",".join(fileStructure.lsFolders("./")))
    bar
    """
    folders = []
    for path in self.ls(subfolder):
      if os.path.isdir(self.getPathInStructure(path)):
        folders.append(os.path.normpath(path))
    return folders

  def exists(self,path):
    """
    >>> from subuserlib.classes.fileStructure import FileStructure
    >>> fileStructure = BasicFileStructure("/home/travis/hashtest")
    >>> fileStructure.exists("./blah")
    True
    >>> fileStructure.exists("./non-existant")
    False
    """
    return os.path.exists(self.getPathInStructure(path))

  def read(self,path):
    """
    >>> from subuserlib.classes.fileStructure import FileStructure
    >>> fileStructure = BasicFileStructure("/home/travis/hashtest")
    >>> print(fileStructure.read("./blah"))
    blahblah
    <BLANKLINE>
    """
    with open(self.getPathInStructure(path),"r") as fd:
      return fd.read()

  def getMode(self,path):
    """
    >>> from subuserlib.classes.fileStructure import FileStructure
    >>> fileStructure = BasicFileStructure("/home/travis/hashtest")
    >>> print(fileStructure.getModeString("./blah"))
    100644
    """
    return os.stat(self.getPathInStructure(path))[stat.ST_MODE]
