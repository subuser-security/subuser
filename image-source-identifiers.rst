Image source identifier paths
--------------------------

When the user wishes to identify a image source, they may refer to the image source using a image source identifier path.  These paths are unicode strings in two formats::

    <image-source-name>@<repository-name>

::

    <image-source-name>@<repository-uri>

In subuser image source names must not contain the character '@'.  Repository names must not contain the character ':', nor may they begin with the character `/`.

It is therefore easy to parse a image source identifier path.  Simply take any text up till the '@' and call it the image source name.  The text following the '@' is set asside as the repository identifier.

If the repository identifier contains a ':' then it is the URI of a remote repository.  If the repository identifier starts with a `/`, it is the path to a local folder.  Otherwise it is the name of a local repository.

Each URI has a context repository. For example, when resolving a subuser image source URI at the command line, the context repository is ``default``.  When resolving a URI appended to ``FROM-SUBUSER-IMAGE`` the context repository is the repository of the subuser image source currently being built.

If a URI contains no '@' then the URI is the name of an image source found in the current context repository.

