#!/bin/bash
/pwd/test/prepare-test-repos.sh
/pwd/logic/subuser subuser --accept add dependent dependent@file:///$TEXTTEST_SANDBOX/test-repos/remote-test-repo > /dev/null 2> /dev/null
/pwd/logic/subuser update lock-subuser-to dependent HEAD > /dev/null 2> /dev/null
cat > /$TEXTTEST_SANDBOX/test-repos/remote-test-repo/dependent/permissions.json <<EOF
{
"user-dirs":["Images","Downloads"]
}
EOF
cd /$TEXTTEST_SANDBOX/test-repos/remote-test-repo/
git add . > /dev/null 2> /dev/null
git commit -m "Change permissions of dependent." > /dev/null 2> /dev/null
cd /$TEXTTEST_SANDBOX
/pwd/logic/subuser $@
