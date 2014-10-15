import sys,os,inspect,site

def getSubuserDir():
  """ Get the toplevel directory for subuser. """
  return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))) # BLEGH!

site.addsitedir(os.path.join(getSubuserDir(),"logic"))

