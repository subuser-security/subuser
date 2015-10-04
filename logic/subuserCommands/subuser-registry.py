#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

try:
  import pathConfig
except ImportError:
  pass
#external imports
import sys
import optparse
import os
import select
import json
#internal imports
import subuserlib.commandLineArguments
from subuserlib.classes.user import User
import subuserlib.profile
import subuserlib.registry

#####################################################################################

def parseCliArgs(realArgs):
  usage = "usage: subuser registry [options]"
  description = """Interact with the subuser registry.

  log
      Prints a log of recent .

  rollback HASH
      Subuser's undo function.  Roll back to an old version of your subuser configuration.  Find the commit hash using subuser update log.  Note: This command is less usefull than lock-subuser-to.

  livelog
      Prints the hash of each new commit to the registry to standard output as the hashes appear. Type q <newline> to exit.
"""
  parser=optparse.OptionParser(usage=usage,description=description,formatter=subuserlib.commandLineArguments.HelpFormatterThatDoesntReformatDescription())
  parser.add_option("--json",dest="json",action="store_true",default=False,help="Print output in machine readable json format.")
  return parser.parse_args(args=realArgs)

#################################################################################################

@subuserlib.profile.do_cprofile
def registry(realArgs):
  """
  Interact with the subuser registry.
  """
  options,args = parseCliArgs(realArgs)
  user = User()
  if len(args) < 1:
    sys.exit("No arguments given. Please use subuser registry -h for help.")
  elif ["log"] == args:
    subuserlib.registry.showLog(user)
  elif "rollback" == args[0]:
    try:
      commit = args[1]
    except KeyError:
      sys.exit("Wrong number of arguments.  Expected a commit.  Try running \nsubuser regsitry --help\nfor more info.")
    with user.getRegistry().getLock():
      subuserlib.registry.rollback(user,commit=commit)
  elif ["live-log"] == args:
    liveLogPath=os.path.join(user.homeDir,".subuser/registry-live-log")
    try:
      os.mkfifo(liveLogPath)
    except OSError:
      pass
    # Why use os.open? http://stackoverflow.com/questions/5782279/why-does-a-read-only-open-of-a-named-pipe-block
    liveLog = os.open(liveLogPath, os.O_RDONLY|os.O_NONBLOCK)
    liveLog = os.fdopen(liveLog)
    q = False
    while not q:
      ready,_,_ = select.select([sys.stdin,liveLog],[],[])
      for selection in ready:
        if selection == liveLog:
          line = liveLog.readline()
          if not line:
            liveLog.close()
            liveLog = os.open(liveLogPath, os.O_RDONLY|os.O_NONBLOCK)
            liveLog = os.fdopen(liveLog)
            break
          if options.json:
            print(line)
          else:
            try:
              announcement = json.loads(line)
              print(announcement["commit"])
            except ValueError:
              pass
        elif selection == sys.stdin:
          if "q" in sys.stdin.readline():
            q = True
            break
        else:
          raise Exception("IMPOSSIBLE!"+str(selection))
    liveLog.close()
    os.remove(liveLogPath)
    sys.exit()
  elif len(args) == 1:
    sys.exit(" ".join(args) + " is not a valid registry subcommand. Please use subuser registry -h for help.")
  else:
    sys.exit(" ".join(args) + " is not a valid registry subcommand. Please use subuser registry -h for help.")

if __name__ == "__main__":
  try:
    registry(sys.argv[1:])
  except KeyboardInterrupt:
    pass
