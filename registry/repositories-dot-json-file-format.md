The repositories.json file format
--------------------------------

In the context of subuser, a `repositories.json` file is a file which describes where subuser programs may be installed from.

The `repositories.json` files are to be arranged into a hierarchy.  Subuser will build the repository list by first looking in the file `~/.subuser/registry/repositories.json` then adding an additional `system repositories` found in:

 * `/etc/subuser/repositories.json`

 * `$SUBUSERDIR/repositories.json`

`$SUBUSERDIR` is the directory where the subuser source resides.

Each repositories.json file is to be a valid [json](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf) file containing a single json object.

This object is a set of key value pairs where each key is the identifier of a subuser repository.

Each identity can either be:
 * string - for a named repository
 * number - for an annonymous repository

Repository names must not contain any of the following characters: `\`,`:` .

The value is a json object with the following properties:

Properties:
-----------

 * `git-origin`: The URI of the repositories git origin.

 Ex:

 ````
 "git-origin" : "$SUBUSERDIR/programsThatCanBeInstalled/"
 ````

Example repositories.json file:

````
{
 "default" : {"git-origin" : "https://github.com/subuser-security/subuser-default-repository.git/"}
}
````

This file states that there is one repository named `default` which was downloaded from `https://github.com/subuser-security/subuser-default-repository.git/`.
