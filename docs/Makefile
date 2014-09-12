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
	docker run -i -t --user=1000 -v $(PWD):/home/sphynx-user -w /home/sphynx-user docs-build-environment /bin/bash

html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) . $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

clean:
	rm -rf _build/
