The permissions.json file format
-------------------------------

A permissions.json file is a file which describes the rights or permissions of a given subuser.  These permissions pertain mainly to that image's ability to interact with it's host operating system.

Each permissions.json file is to be a valid [json](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf) file containing a single json object.

The json object MUST have the following fields:
-----------------------------------------

 * `description`: This field describes what the subuser is/what it does.

  Ex:

  ````json
   "description"                : "Simple universal text editor."
  ````

 * `maintainer`: This field marks who is responsible for the `permissions.json` file, and accompanying `Dockerfile`.  It does NOT mark who is responsible for the image itself.

  Ex:
  
  ````json
   ,"maintainer"                : "Timothy Hobbs <timothyhobbs (at) seznam dot cz>"
  ````

The json object MAY at your option contain the following additional fields:
---------------------------------------------------------------------------

**Note on optional fields**: Setting an optional field to an empty string is not a valid way of requesting it's default value.  If you want the default value, don't include the field at all.

Permissions are categorized into 4 levels of permissiveness:

 1. conservative: These permissions should be 100% safe in all cases.
 2. moderate: These permissions have the potential to give the subuser access to some user data but not all.
 3. liberal: These permissions give the subuser access to some or all user data, and/or present a significantly increased risk of the subuser breaking out of the container.
 4. anarchistic: These permissions give the subuser full access to the system.

Conservative permissions
------------------------

 * `last-update-time`: This field records the last time the image, or it's `Dockerfile` were known to be updated.  The purpose of this field is telling `subuser` if a image has been updated and must be re-installed.  It is important that this string be comparable with python's built in string comparison algorithm.

  Ex:

  ````json
   ,"last-update-time"          : "2014-02-12-12:59"
  ````

 * `executable`: This field denotes the absolute path within the Docker image where the given image's executable resides.

  Ex:

  ````json
   ,"executable"                : "/usr/bin/vim"
  ````

 **Default**: The image has no executable and cannot be run(but it can be depended upon, as a library).

 * `basic-common-permissions`: This flag allows you to enable a set of basic, safe, and common permissions without having to list them individualy.  The basic common permissions are:

  - `stateful-home`
  - `inherit-locale`
  - `inherit-timezone`

  If any of the basic common permissions are also set, their value over-rides this value.  For example, if `stateful-home` is explicitly set to `false` but `basic-common-permissions` is set to `true`, `stateful-home` is `false`.

 * `stateful-home`: Changes that the subuser makes to it's home directory should be saved to a special subuser-homes directory.

  ````json
   ,"stateful-home"             : false
  ````

  **Default**: `false`

 * `inherit-locale`: Automatically set the $LANG and $LANGUAGE environment variable in the container to the value outside of the container. Note: You do not have to set this if you have set `basic-common-permissions`.

  ````json
   ,"inherit-locale"             : true
  ````

  **Default**: `false`

 * `inherit-timezone`: Automatically set the $TZ environment variable in the container to the value outside of the container.  Give the sub user read only access to the `/etc/localtime` file. Note: You do not have to set this if you have set `basic-common-permissions`.

  ````json
   ,"inherit-timezone"             : true
  ````

  **Default**: `false`

Moderate permissions
--------------------

 * `user-dirs`: A list of relative paths to user directories which are to be shared between the host and the given image. The subuser is given read-write access to any user directories listed.

  Ex:

  ````json
   ,"user-dirs"                 : ["Downloads"]
  ````

  In this example, the subuser is able to access the `~/Downloads` directory on the host. 


  **Default**: `[]`

 * `sound-card`:  The subuser is allowed to access the soundcard on the host.

Warning: This means, not only can the subuser play sounds, but it may listen to your microphone too!

  Ex:

  ````json
   ,"sound-card"                : true
  ````

  **Default**: `false`

 * `webcam`: The subuser is allowed to access the computer's webcam/USB webcams.

  Ex:

  ````json
   ,"webcam"                     : true
  ````

  **Default**: `false`

 * `access-working-directory`: The subuser is given read-write access to the host user's current working directory.

  Ex:

  ````json
   ,"access-working-directory" : true
  ````

  **Default**: `false`

 * `allow-network-access`: Should the subuser be allowed to access the network/internet?

  Ex:

  ````json
   ,"allow-network-access"      : false
  ````

  **Default**: `false`

Liberal permissions
-------------------

 * `x11`: The subuser is allowed to interact with the x11 server on the host.

  Note: Known to be insecure!

  Ex:

  ````json
   ,"x11"                       : true
  ````

  **Default**: `false`

 * `graphics-card`: The subuser is allowed to access the graphics-card directly(OpenGL).

  Ex:

  ````json
   ,"graphics-card"                       : true
  ````

  **Default**: `false`

 * `serial-devices`: The subuser is allowed to access serial devices: `/dev/ttyACM*`, `/dev/ttyUSB*`, and `/dev/ttyS*`.

  Ex:

  ````json
   ,"serial-devices"                     : true
  ````

  **Default**: `false`

 * `system-dbus`: Should the subuser be allowed to communicate with the system wide dbus daemon?

  Ex:

  ````json
   ,"system-dbus"              : false
  ````

  **Default**: `false`

 * `as-root`: Run the subuser as the root user within the container.

 Ex:

 ````json
  ,"as-root"                     : true
 ````

 **Default**: `false`

 * `sudo`: Grant the subuser sudo privileges within the container.

 Ex:

 ````json
  ,"sudo"                     : true
 ````

 **Default**: `false`


Anarchistic permissions
-----------------------

 * `privileged`: Should the subuser's Docker container be run in `privileged` mode?

  **Note**: Completely insecure!

  Ex:

  ````json
   ,"privileged"                : false
  ````

  **Default**: `false`
