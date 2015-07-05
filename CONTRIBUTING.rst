Contributing
------------

Changes should be submitted in the form of a pull request.  If you do not have a github account, pull requests may be sent to the timothyhobbs@seznam.cz

There is no need to sign a contributor agreement.  All changes bellong to you and you agree to provide them to the world under the conditions of the LGPLv3 or later license agreement.

Coding guidelines
-----------------

 * One of the major aims of this project is to be as easy to install as possible while still maintaining a maintainable code base.  For this reason, I have chosen to aim for compatibility with all python versions later than 2.7 including the 3.x range.  Furthermore, there are to be NO EXTERNAL DEPENDENCIES!

 * Do not maintain 80 collumn code formatting.  Any pull requests to refill to 80 collumns will be rejected.  Refilling is based on some meaningless and ancient standard.  I often use 60 collumn terminals which make 80 collumns hard to read, it is far easier to read line wrapped code that is of its natural length then to read line-wrapped filled code.

 * Before writting comments read `this article <http://rhodesmill.org/brandon/2012/one-sentence-per-line/>`_

 * Imports should be grouped into two groups.  The first group is for external imports, like importing modules from the standard library.  The seccond group is for subuser specific modules.  You can see how I do it by looking at one of the existing modules.

 * Indentation is done with two spaces.

 * Tabs are forbidden.

 * Use human readable names for things.

 * Do not shorten words/leave out vowels.

   + There are a few cases in which I have used shortened versions of things: ``dir`` for directory, ``arg`` for argument.  These are cases where the short version is as widely known as the long version.

