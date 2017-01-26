Screenshots
-----------

Programs don't look much different when running under subuser. So there's not much to see.

.. image:: ./screenshots/liferea+firefox.png

However, notice that my ``firefox`` subuser has different settings and different plugins installed than my ``google-calendar`` subuser. Also note that the ``firefox`` subuser has a pink border, where-as the ``google-calendar`` subuser has a green one. This allows you to easilly distinguish between windows from different subusers which reduces the chance of subusers sneakily fishing for your keystrokes.

.. image:: ./screenshots/emacs+texttest.png

Subuser itself is developed in emacs running in subuser. The test suit also runs within subuser.

.. image:: ./screenshots/libreoffice.png

Libreoffice also works in subuser as do most programs. Note that only files and folders in the $PWD from wich libreoffice was launched are accessible.
