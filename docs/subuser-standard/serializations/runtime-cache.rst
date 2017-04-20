Runtime cache
-------------

The ``runtime-cache`` directory caches information used by subuser while prepairing subusers to be run.

The directory contains a set of subdirectories each named with the Docker image Id of a given installed-image.

Each image directory contains a set of JSON files named with the SHA512 hash of the ``permissions.json`` file that was used to generate the runtime and postfixed with ``.json``.

In summary, the path to a given runtime config might look like ``$HOME/.subuser/runtime-cache/<Docker-image-Id>/<hash-of-runready-image-preparation-Dockerfile>.json``.

Each permissions-specific JSON file caches information needed to run a specific installed subuser image with a specific set of permissions. Each permissions specific JSON file is a valid JSON file containing a single JSON object with the following properites:

 * ``run-ready-image-id`` - the Docker image Id of the image which was prepaired for running that subuser.
.

