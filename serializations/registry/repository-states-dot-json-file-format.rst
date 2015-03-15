The repository-states.json file format
======================================

In the context of subuser, a ``repository-states.json`` file is a file which serializes the mutable state of each subuser repository.

Unlike ``repositories.json`` this is a per-user file which is non-hierarchical.

Each repository-states.json file is to be a valid `json <http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf>`_ file containing a single json object.

This object is a set of key value pairs where each key is the identifier of a subuser repository.

Repositories which the user has yet to initialize(by installing a image from that repository) are not represented in this file.

Each repository identifier can either be:
 * string - for a named repository
 * number - for an annonymous repository

Repository names must not contain any of the following characters: ``\``, ``:`` .

The value is a json object with the following properties:

Properties
----------

 * ``git-commit-hash``: The hash of the currently checked out commit of the subuser repository.  Specifically, this is the output of ``git show-ref -s HEAD`` when run within the given repository's git repository. If the repository is not managed by git, this attribute may be set to ``nil``.

  Ex::

   "git-commit-hash" : "a88ce1ec812fec3072b255d7ef7aa53f281d1dcf"

