Program source identifier paths
--------------------------

When the user wishes to identify a program source, they may refer to the program source using a program source identifier path.  These paths are unicode strings in two formats:

````
<progam-source-name>@<repository-name>
````

````
<program-source-name>@<repository-uri>
````

In subuser progam source names must not contain the character '@'.  Repository names must not contain the character ':'.

It is therefore easy to parse a program source identifier path.  Simply take any text up till the '@' and call it the program source name.  The text following the '@' is set asside as the repository identifier.

If the repository identifier contains a ':' then it is the URI of a remote repository.  Otherwise it is the name of a local repository.
