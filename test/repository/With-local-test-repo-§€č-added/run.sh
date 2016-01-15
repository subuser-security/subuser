#!/bin/bash
/pwd/test/prepare-test-repos.sh
/pwd/logic/subuser repository add §€č /$TEXTTEST_SANDBOX/test-repos/local-test-repo-§€č > /dev/null 2> /dev/null
/pwd/logic/subuser $@
