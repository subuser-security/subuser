The permissions.json file format
-------------------------------

A permissions.json file is a file which describes the rights or permissions of a image running within a docker container.  These permissions pertain mainly to that image's ability to interact with it's host operating system.

Each permissions.json file is to be a valid [json](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf) file containing a single json object.

The json object MUST have the following fields:
-----------------------------------------

 * `description`: This field describes what the image is/what it does.

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

 * `user-dirs`: A list of relative paths to user directories which are to be shared between the host and the given image. The image is given read-write access to any user directories listed.

  Ex:

  ````json
   ,"user-dirs"                 : ["Downloads"]
  ````

  In this example, the image is able to access the `~/Downloads` directory on the host. 


  **Default**: `[]`

 * `x11`: The image is allowed to interact with the x11 server on the host.

  Note: Known to be insecure!

  Ex:

  ````json
   ,"x11"                       : true
  ````

  **Default**: `false`

 * `graphics-card`: The image is allowed to access the graphics-card directly(OpenGL).

  Ex:

  ````json
   ,"graphics-card"                       : true
  ````

  **Default**: `false`

 * `sound-card`:  The image is allowed to access the soundcard on the host.

Warning: This means, not only can the image play sounds, but it may listen to your microphone too!

  Ex:

  ````json
   ,"sound-card"                : true
  ````

  **Default**: `false`

 * `webcam`: The image is allowed to access the computer's webcam/USB webcams.

  Ex:

  ````json
   ,"webcam"                     : true
  ````

  **Default**: `false`

 * `inherit-working-directory`: The image is given read-write access to the host user's current working directory.

  Ex:

  ````json
   ,"inherit-working-directory" : true
  ````

  **Default**: `false`

 * `allow-network-access`: Should the image be allowed to access the network/internet?

  Ex:

  ````json
   ,"allow-network-access"      : false
  ````

  **Default**: `false`

 * `stateful-home`: Changes that the image makes to it's home directory should be saved to a special subuser-homes directory.

  ````json
   ,"stateful-home"             : false
  ````

  **Default**: `true`

 * `as-root`: Run the image as the root user within the container.

 Ex:

 ````json
  ,"as-root"                     : true
 ````

 **Default**: `false`

 * `privileged`: Should the image's Docker container be run in `privileged` mode?

  **Note**: Completely insecure!

  Ex:

  ````json
   ,"privileged"                : false
  ````

  **Default**: `false`
