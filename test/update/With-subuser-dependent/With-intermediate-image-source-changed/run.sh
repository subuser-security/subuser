#!/bin/bash
/pwd/test/prepare-test-repos.sh
/pwd/logic/subuser subuser --accept add dependent dependent@file:///$TEXTTEST_SANDBOX/test-repos/remote-test-repo > /dev/null 2> /dev/null
cat > /$TEXTTEST_SANDBOX/test-repos/remote-test-repo/images/intermediary/image/SubuserImagefile <<EOF
FROM-SUBUSER-IMAGE dependency2
EOF
cd /$TEXTTEST_SANDBOX/test-repos/remote-test-repo/
git add . > /dev/null 2> /dev/null
git commit -m "Changed dependency of intermediary image." > /dev/null 2> /dev/null
cd /$TEXTTEST_SANDBOX
/pwd/logic/subuser $@
