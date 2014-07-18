The repositories.json file format
--------------------------------

In the context of subuser, a `repositories.json` file is a file which describes where subuser programs may be installed from.

The `repositories.json` files are to be arranged into a hierarchy.  Subuser will build the repository list by first looking in the file `~/.subuser/repositories.json` then adding an additional repositories found in:

 * `/etc/subuser/repositories.json`

 * `$SUBUSERDIR/repositories.json`

`$SUBUSERDIR` is the directory where the subuser source resides.

Each repositories.json file is to be a valid [json](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf) file containing a single json object.

This object is a set of key value pairs where each key is the name of a subuser repository.  Repository names must not contain the `\` character.  The value is a json object with the following properties:

Properties:
-----------

 * `git-origin`: The URI of the repositories git origin.

 Ex:

 ````
 "git-origin" : "$SUBUSERDIR/programsThatCanBeInstalled/"
 ````

 * `auto-remove`: If only one installed image was built from this repository and that image is uninstalled, remove this repository.

 Ex:

 ````
 "auto-remove" : true
 ````



Example repositories.json file:

````
{
 "default" : {"git-origin" : "https://github.com/subuser-security/subuser-default-repository.git/",
             "auto-remove" : false}
}
````

This file states that there is one repository named `default` which was downloaded from `https://github.com/subuser-security/subuser-default-repository.git/`.
