# Taken from http://code.activestate.com/recipes/576973-getting-the-sha-1-or-md5-hash-of-a-directory/
# http://akiscode.com/articles/sha-1directoryhash.shtml
# Copyright (c) 2009 Stephen Akiki
# MIT License (Means you can do whatever you want with this)
#  See http://www.opensource.org/licenses/mit-license.php
# Error Codes:
#   -1 -> Directory does not exist
#   -2 -> General error (see stack traceback)

def getHashOfDirs(directory, verbose=0):
  """
  Return the SHA1 hash of the directory. Going through the files in the order returned by python's os.walk command. Return the hash as a hexidecimal string.

  >>> getHashOfDirs("/home/travis/hashtest")
  '69858e09f8b90498023c308a1700dcb842e55a0a'
  """
  import hashlib, os
  SHAhash = hashlib.sha1()
  if not os.path.exists (directory):
    return -1

  try:
    for root, dirs, files in os.walk(directory):
      for names in files:
        if verbose == 1:
          print('Hashing', names)
        filepath = os.path.join(root,names)
        try:
          f1 = open(filepath, 'rb')
        except:
          # You can't open the file for some reason
          f1.close()
          continue

        while 1:
          # Read file in as little chunks
          buf = f1.read(4096)
          if not buf:
            break
          SHAhash.update(buf)
        f1.close()

  except:
    import traceback
    # Print the stack traceback
    traceback.print_exc()
    return -2

  return SHAhash.hexdigest()
