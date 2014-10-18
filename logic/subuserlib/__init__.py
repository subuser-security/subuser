"""
Implementation details
======================

It has become abundantly clear, that with enough eyes on the code, all bugs are deep.  Typos and off by one errors will be fixed by people casually browsing the code base, but deeper structural problems will remain. Few read the entire source and fewer still understand its structure.  Over time, these problems worsen as contributors unfamiliar with the code base bolt features on to the side with little planning or understanding.  It is for this reason that I kindly request that you at least attempt to orient yourself with the general layout of the code, before getting out the ducktape.

Class structure
---------------

Subuser is written in Python with an object oriented architecture.  The main data structure in subuser is a tree of objects.  The base object is a C{subuserlib.classes.user.User} object.




"""

__docformat__ = 'restructuredtext en'
