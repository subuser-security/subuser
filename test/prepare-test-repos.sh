#!/bin/bash

# Prepare test repos
git config --global user.email "you@example.com" 2> /dev/null
git config --global user.name "Your Name" 2> /dev/null

cd test-repos/remote-test-repo
git init > /dev/null
git add . > /dev/null
git commit -m 'test' > /dev/null
cd ../..

cd test-repos/default-test-repo
git init > /dev/null
git add . > /dev/null
git commit -m 'test' > /dev/null
cd ../..

cd test-repos/different-sets-of-permissions
git init > /dev/null
git add . > /dev/null
git commit -m 'test' > /dev/null
cd ../..

cd test-repos/version-constrained-test-repo
git init > /dev/null
git add . > /dev/null
git commit -m 'test' > /dev/null
git checkout -b subuser-0.5 > /dev/null 2> /dev/null
echo {} > .subuser.json
git mv bip bop > /dev/null
git add . > /dev/null
git commit -m 'change bip to bop' > /dev/null
git checkout master > /dev/null 2> /dev/null
git mv bip baz > /dev/null
git add . > /dev/null
git commit -m 'change bop to baz' > /dev/null
cd ../..
