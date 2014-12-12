#!/usr/bin/env python # This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
Contains code that prepairs a subuser's image to be run.
"""

#external imports
import sys,os,getpass
#internal imports
#import ...


def generateImagePreparationDockerfile(subuserToRun):
  """
  There is still some preparation that needs to be done before an image is ready to be run.  But this preparation requires run time information, so we cannot preform that preparation at build time.
  """
  dockerfileContents  = "FROM "+subuserToRun.getImageId()+"\n"
  dockerfileContents += "RUN useradd --uid="+str(os.getuid())+" "+getpass.getuser()+" ;export exitstatus=$? ; if [ $exitstatus -eq 4 ] ; then echo uid exists ; elif [ $exitstatus -eq 9 ]; then echo username exists. ; else exit $exitstatus ; fi\n"
  dockerfileContents += "RUN test -d /home/"+getpass.getuser()+" || mkdir /home/"+getpass.getuser()+" && chown "+getpass.getuser()+" /home/"+getpass.getuser()+"\n"
  if subuserToRun.getPermissions()["serial-devices"]:
    dockerfileContents += "RUN groupadd dialout; export exitstatus=$? ; if [ $exitstatus -eq 4 ] ; then echo gid exists ; elif [ $exitstatus -eq 9 ]; then echo groupname exists. ; else exit $exitstatus ; fi\n"
    dockerfileContents += "RUN groupadd uucp; export exitstatus=$? ; if [ $exitstatus -eq 4 ] ; then echo gid exists ; elif [ $exitstatus -eq 9 ]; then echo groupname exists. ; else exit $exitstatus ; fi\n"
    dockerfileContents += "RUN usermod -a -G dialout "+getpass.getuser()+"\n"
    dockerfileContents += "RUN usermod -a -G uucp "+getpass.getuser()+"\n"
  if subuserToRun.getPermissions()["sudo"]:
    dockerfileContents += "RUN (umask 337; echo \""+getpass.getuser()+" ALL=(ALL) NOPASSWD: ALL\" > /etc/sudoers.d/allowsudo )\n"
  return dockerfileContents

def buildRunReadyImageForSubuser(subuserToRun):
  """
  Returns the Id of the Docker image to be run.
  """
  imageId = subuserToRun.getUser().getDockerDaemon().build(None,quietClient=True,useCache=True,forceRm=True,rm=True,dockerfile=generateImagePreparationDockerfile(subuserToRun))
  return imageId

