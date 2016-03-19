#!/bin/bash
/pwd/test/prepare-test-repos.sh
/pwd/logic/subuser subuser add foo "image source with spaces@$TEXTTEST_SANDBOX/test-repos/local-test-repo-§€č"
