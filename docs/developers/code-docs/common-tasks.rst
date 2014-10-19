Common coding tasks
-------------------

Adding a new permission
***********************

To add a new permission, you first need to get the new permisison accepted into `the subuser standard <https://github.com/subuser-security/subuser-standard>`_ via pull request.

Once it is accepted:

 1. Set the permission's default value in the `permissions module <https://github.com/subuser-security/subuser/blob/master/logic/subuserlib/permissions.py>`_

 2. Tell subuser how to apply the permission in the `run module <https://github.com/subuser-security/subuser/blob/master/logic/subuserlib/run.py>`_

 3. Describe the permission in the `permissions class module <https://github.com/subuser-security/subuser/blob/master/logic/subuserlib/classes/permissions.py>`_

That was easy, wasn't it?

