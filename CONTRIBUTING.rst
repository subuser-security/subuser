Contributing
------------

Changes should be submitted in the form of a pull request.  If you do not have a github account, pull requests may be sent to the timothyhobbs@seznam.cz

There is no need to sign a contributor agreement.  All changes belong to you and you agree to provide them to the world under the conditions of the LGPLv3 or later license agreement.

Coding guidelines
-----------------

* One of the major aims of this project is to be as easy to install as possible while still providing a maintainable code base. At first I banned all external dependencies, fearing constant breakage and incompatibilities. However, I have grown to trust the pypi community a bit, and now only strongly discourage new external dependencies.

* Do not maintain 80 column code formatting.  Any pull requests to refill to 80 columns will be rejected.  Refilling is based on some meaningless and ancient standard.  I often use 60 column terminals which make 80 columns hard to read, it is far easier to read line wrapped code that is of its natural length then to read line-wrapped filled code.

* Before writing comments read `this article <http://rhodesmill.org/brandon/2012/one-sentence-per-line/>`_

* Imports should be grouped into two groups.  The first group is for external imports, like importing modules from the standard library.  The second group is for subuser specific modules.  You can see how I do it by looking at one of the existing modules.

* Indentation is done with two spaces.

* Tabs are forbidden.

* Use human readable names for things.

* Do not shorten words/leave out vowels.

  + There are a few cases in which I have used shortened versions of things: ``dir`` for directory, ``arg`` for argument.  These are cases where the short version is as widely known as the long version.
