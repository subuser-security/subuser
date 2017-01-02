#!/usr/bin/python3
# -*- coding: utf-8 -*-
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
def runCommand(realArgs):
  """
  Interact with the subuser registry.
  """
  options,args = parseCliArgs(realArgs)
  user = User()
  user.getRegistry().commit_message = " ".join(["subuser","repository"]+realArgs)
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
      if not user.getRegistry().getGitRepository().doesCommitExist(commit):
        sys.exit("The commit "+commit+" does not exist. Use --help for help.")
      subuserlib.registry.rollback(user,commit=commit)
  elif ["live-log"] == args:
    liveLogDir = os.path.join(user.homeDir,".subuser/registry-live-log")
    liveLogPath = os.path.join(liveLogDir,str(os.getpid()))
    if not os.path.exists(liveLogDir):
      user.getEndUser().makedirs(liveLogDir)
    os.mkfifo(liveLogPath)
    user.getEndUser().chown(liveLogPath)
    # Why use os.open? http://stackoverflow.com/questions/5782279/why-does-a-read-only-open-of-a-named-pipe-block
    liveLog = os.open(liveLogPath,os.O_RDONLY|os.O_NONBLOCK)
    q = False
    line = ""
    while not q:
      ready,_,_ = select.select([sys.stdin,liveLog],[],[])
      for selection in ready:
        if selection == liveLog:
          line += os.read(liveLog,1)
          try:
            announcement = json.loads(line)
            if options.json:
              print(line)
            else:
              print("New commit to registry:" + announcement["commit"])
            line = ""
          except ValueError:
            pass
        elif selection == sys.stdin:
          stdinLine = sys.stdin.readline()
          if "q" in stdinLine or not stdinLine:
            q = True
            print("Quitting...")
            break
        else:
          raise Exception("IMPOSSIBLE!"+str(selection))
    os.close(liveLog)
    os.remove(liveLogPath)
    sys.exit()
  elif len(args) == 1:
    sys.exit(" ".join(args) + " is not a valid registry subcommand. Please use subuser registry -h for help.")
  else:
    sys.exit(" ".join(args) + " is not a valid registry subcommand. Please use subuser registry -h for help.")
