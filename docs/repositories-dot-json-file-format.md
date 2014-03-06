The repositories.json file format
--------------------------------

In the context of subuser, a `repositories.json` file is a file which describes where subuser programs may be installed from.

The `repositories.json` files are to be arranged into a fallback-hierarchy.  Subuser will first look up properties in the file `~/.subuser/repositories.json` falling back to:

 * `/etc/subuser/repositories.json`

 * `$SUBUSERDIR/repositories.json`

`$SUBUSERDIR` is the directory where the subuser source resides.  It corresponds to the root of this git repository.


Each repositories.json file is to be a valid [json](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf) file containing a single json object.

This object is a set of key value pairs where each key is the name of a subuser repository.  The value is a json object with the following properties:

Properties:
-----------
**Note on paths**: Each path is to be absolute.  Any environment variables of the form `$VARIABLE_NAME` will be expanded.

 * `path`: The path to the repository.

 Ex:

 ````
 "path" : "$SUBUSERDIR/programsThatCanBeInstalled/"
 ````

Example repositories.json file:

````
{
 "default" : {"path" : "$SUBUSERDIR/programsThatCanBeInstalled/"}
}
````

This file states that there is one repository named `default` which can be found in the `$SUBUSERDIR/programsThatCanBeInstalled` directory.
