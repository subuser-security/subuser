# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = _build

.docs-build-environment: Dockerfile
	docker build -t docs-build-environment .
	touch .docs-build-environment

shell: .docs-build-environment
	docker run -i -t --user=1000 -v $(PWD)/..:/home/sphynx-user -w /home/sphynx-user/docs -e HOME=/home/sphynx-user/ docs-build-environment /bin/bash

command-docs:
	cd commands ; ./generate-command-docs.py
	echo DONE GENERATING COMMAND DOCS

pylint:
	cd ../logic ; pylint --disable=C0111,C0301,C0103,C0322,C0323,C0324,R0913,R0903,R0904,superfluous-parens,bad-continuation,unused-variable,too-many-branches,too-many-locals,bad-builtin,deprecated-lambda,locally-disabled --indent-string='  ' subuserlib/ > ../docs/developers/pylint.rst ; echo DONE GENERATING PYLINT OUTPUT
	./developers/restructure-pylint-output

images-dir:
	mkdir developers/images ; echo IMAGES DIR CREATED

developers/images/object-hierarchy.png: developers/object-hierarchy.uxf images-dir
	umlet -action=convert -format=png -filename=developers/object-hierarchy.uxf -output=developers/images/object-hierarchy


html: command-docs pylint community.rst developers/contributing.rst developers/images/object-hierarchy.png
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) . $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

clean:
	rm -rf _build/
