#!/bin/bash
/pwd/test/prepare-test-repos.sh
/pwd/logic/subuser subuser --accept add supa all-permissions@file:///$TEXTTEST_SANDBOX/test-repos/different-sets-of-permissions > /dev/null 2> /dev/null
/pwd/logic/subuser $@
