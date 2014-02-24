VERSION 0.2
-------------

* OpenGL support

* Refactor/improved install code: allow multiple programs to be installed with one command: issue #8

* Split: install to command and common function files: issue #84#issuecomment-35587683

* Refactor code indention: added module to do so: issue #86

* Add the describe command

* FIX: The mark-as-needing-update command messes up the order of attributes in permissions.json #32

* Implemented new installed-programs.json format: issue #63

* Refactored/Added getRegistry and getInstalledPrograms to a list like: getAvailablePrograms and added #75

* Added: new command 'print-dependency-matrix' Which can take similar to 'list' the arguments: available, installed or a list of subuser-programs

* Improved Python Files I/O code

* Simplify some code dict.iteritems to dict.keys where applicable

* Implemented install-from-registry command which installs all of the programs listed in installed-programs.json file. #23

* Refactor some print statements
  issue #51
  
* Implemented option to build base docker images from within subuser: 
  for examples see: (https://github.com/subuser-security/subuser-examples)
  issue #24, #49, #45, #41
  
* Added ability to print the dependency tree of any subuser program

* Refactor help code and improved output

* subuser list available now includes information about each program in the listing output.

* The last-update-time attribute in permissions.json is now optional.  You can easilly mark a program as needing to be updated with the command "subuser mark-as-needing-update program-name"

* Can now set a container as privileged within the permissions.json file.

* Refactor code and simplify usage of subprocess.check_call

* If an image required for running a program dissapears, ask the user if they want it automatically re-installed.

* Set the TERM variable in appropriate places in Dockerfiles.

* Got sound working thanks to [peter1000](https://github.com/timthelion/subuser/pull/22)

VERSION 0.1
-------------
start of changelog
