Image source identifier paths
--------------------------

When the user wishes to identify a image source, they may refer to the image source using a image source identifier path.  These paths are unicode strings in two formats:

````
<image-source-name>@<repository-name>
````

````
<image-source-name>@<repository-uri>
````

In subuser image source names must not contain the character '@'.  Repository names must not contain the character ':'.

It is therefore easy to parse a image source identifier path.  Simply take any text up till the '@' and call it the image source name.  The text following the '@' is set asside as the repository identifier.

If the repository identifier contains a ':' then it is the URI of a remote repository.  Otherwise it is the name of a local repository.
