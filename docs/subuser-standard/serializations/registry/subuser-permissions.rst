The permissions.json and permissions-template.json files
--------------------------------

The registry contains a subdirectory, ``permissions`` which contains a subdirectory for each subuser. Each subuser's permissions subdirectory contains two files:

``permissions.json`` - This file contains the list of permissions which has been approved by the user.

``permissions-template.json`` - This file contains the permissions template which was used to suggest to the user which permissions to choose. This permissions template is copied from the subuser's image source each time the image source's permissions are updated.
