#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

try:
  import pathConfig
except ImportError:
  pass
#external imports
import sys
import os
#internal imports
import subuserlib.classes.user
import subuserlib.profile

##############################################################
helpString = """
Display the command which would be issued to launch Docker if you were to run this subuser.

For example:

    $ subuser dry-run iceweasel

Will display the command used to launch the subuser iceweasel.

Please note, this is only a rough approximation for debugging purposes and there is no guarantee that the command displayed here would actually work.
"""

#################################################################################################
def dryRunTestSetup():
  import sys,os,getpass
  os.getuid = lambda: 1000
  getpass.getuser = lambda: "travis"

@subuserlib.profile.do_cprofile
def dryRun(args):
  """
  Print the command that would have been run if this wasn't a dry run.

  >>> dry_run = __import__("subuser-dry-run")
  >>> dry_run.dryRunTestSetup()
  >>> subuser = __import__("subuser-subuser")
  >>> remove_old_images = __import__("subuser-remove-old-images")

  If we dry run the basic foo test subuser, we will see the generated pre-run Dockerfile and also the docker command that will launch our subuser.

  >>> dry_run.dryRun(["foo"])
  The image will be prepared using the Dockerfile:
  FROM 2
  RUN useradd --uid=1000 travis ;export exitstatus=$? ; if [ $exitstatus -eq 4 ] ; then echo uid exists ; elif [ $exitstatus -eq 9 ]; then echo username exists. ; else exit $exitstatus ; fi
  RUN test -d /home/travis || mkdir /home/travis && chown travis /home/travis
  <BLANKLINE>
  The command to launch the image is:
  docker 'run' '--rm' '-i' '-e' 'HOME=/home/travis' '--workdir=/home/travis' '--net=none' '--user=1000' '--hostname' '<random-hostname>' '--entrypoint' '/usr/bin/foo' '3'

  Running subusers installed through temporary repositories works as well.  Here, we add a subuser named bar, run it, and then remove it again.

  >>> subuser.subuser(["add","bar","--accept","bar@file:///home/travis/remote-test-repo"])
  Adding subuser bar bar@file:///home/travis/remote-test-repo
  Adding new temporary repository file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  bar would like to have the following permissions:
   Description: bar
   Maintainer: fred
   Executable: /usr/bin/bar
  A - Accept and apply changes
  E - Apply changes and edit result
  A
  Checking if images need to be updated or installed...
  Checking if subuser bar is up to date.
  New images for the following subusers need to be installed:
  bar
  Installing bar ...
  Building...
  Building...
  Building...
  Successfully built 4
  Building...
  Building...
  Building...
  Successfully built 5
  Installed new image <5> for subuser bar
  Running garbage collector on temporary repositories...

  The actual dry-run call.

  >>> dry_run.dryRun(["bar"])
  The image will be prepared using the Dockerfile:
  FROM 5
  RUN useradd --uid=1000 travis ;export exitstatus=$? ; if [ $exitstatus -eq 4 ] ; then echo uid exists ; elif [ $exitstatus -eq 9 ]; then echo username exists. ; else exit $exitstatus ; fi
  RUN test -d /home/travis || mkdir /home/travis && chown travis /home/travis
  <BLANKLINE>
  The command to launch the image is:
  docker 'run' '--rm' '-i' '-e' 'HOME=/home/travis' '--workdir=/home/travis' '--net=none' '--user=1000' '--hostname' '<random-hostname>' '--entrypoint' '/usr/bin/bar' '6'

  Cleanup.

  >>> subuser.subuser(["remove","bar"])
  Removing subuser bar
   If you wish to remove the subusers image, issue the command $ subuser remove-old-images
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Running garbage collector on temporary repositories...
  >>> remove_old_images.removeOldImages([])
  Removing unneeded image 5 : bar@file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Running garbage collector on temporary repositories...
  Removing uneeded temporary repository: file:///home/travis/remote-test-repo
  """
  if len(args) == 0 or {"help","-h","--help"} & set(args):
    print(helpString)
    sys.exit()
  subuserName = args[0]
  argsToPassToImage = args[1:]
  user = subuserlib.classes.user.User()
  if subuserName in user.getRegistry().getSubusers():
    subuser = user.getRegistry().getSubusers()[subuserName]
    print("The image will be prepared using the Dockerfile:")
    print(subuser.getRunReadyImage().generateImagePreparationDockerfile())
    print("The command to launch the image is:")
    print(subuser.getRuntime(os.environ).getPrettyCommand(argsToPassToImage))
  else:
    sys.exit(subuserName + " not found.\n"+helpString+"\n The following subusers are available for use:"+str(user.getRegistry().getSubusers().keys()))

if __name__ == "__main__":
  dryRun(sys.argv[1:])
