In order to build the docs, you must have the subuser-standard within the docs directory.  In order to get the subser-standard issue:

    git clone https://github.com/subuser-security/subuser-standard.git

To build the docs, cd to this repositories root, run `subuser dev docs` and run `make html` in the docs directory:

    cd ..
    subuser dev docs
    cd docs
    make html
