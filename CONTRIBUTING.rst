Contributing
------------

Changes should be submitted in the form of a pull request.  If you do not have a github account, pull requests may be sent to the timothyhobbs@seznam.cz

There is no need to sign a contributor agreement.  All changes belong to you and you agree to provide them to the world under the conditions of the LGPL-3.0 license agreement.

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

Maintainers
-----------

As the subuser project is still very small, there is not much of an organizational structure. Maintainers are people who have write access to the main subuser repository. They can review and merge pull requests as well as push commits. Maintainers cannot, however, tag releases. Releases may be tagged by the original author of subuser, Timothy Hobbs, and will be GPG signed by him as well.

There are no clear guidelines on how to become a maintainer. It is expected that the number of maintainers will remain relatively low in the near future. However, there are several things that you should keep in mind if you wish to become a maintainer in the future:

 - Respect the :doc:`community guidelines <../community>`. Don't be racist or sexist or otherwise unacceptable.

 - Don't be pseudonymous. I know that a project like subuser which has security as one of its goals will attract pseudonymous users. However, security is also to some extent a matter of trust. Unfortunately, I cannot accept pseudonymous users as maintainers. You must have a real name associated with your online identity.
