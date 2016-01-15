#!/bin/bash
/pwd/test/prepare-test-repos.sh
/pwd/logic/subuser subuser --accept add foo broken-syntax@file:///$TEXTTEST_SANDBOX/test-repos/remote-test-repo > /dev/null 2> /dev/null
/pwd/logic/subuser $@
