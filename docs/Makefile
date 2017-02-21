# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = _build

subuser-standard/permissions-dot-json-file-format.rst: ../logic/subuserlib/permissions.py
	cd subuser-standard ; ./generate-permissions-rst.py
	echo DONE GENERATING PERMISSION DOCS

command-docs:
	cd commands ; ./generate-command-docs.py
	echo DONE GENERATING COMMAND DOCS

pylint:
	cd ../logic ; pylint --disable=C0111,C0301,C0103,C0322,C0323,C0324,R0913,R0903,R0904,superfluous-parens,bad-continuation,unused-variable,too-many-branches,too-many-locals,bad-builtin,deprecated-lambda,locally-disabled --indent-string='  ' subuserlib/ > ../docs/developers/pylint.rst ; echo DONE GENERATING PYLINT OUTPUT
	./developers/restructure-pylint-output

developers/images:
	mkdir developers/images ; echo IMAGES DIR CREATED

news/images:
	mkdir news/images ; echo IMAGES DIR CREATED

developers/images/object-hierarchy.png: developers/object-hierarchy.uxf developers/images
	umlet -action=convert -format=png -filename=developers/object-hierarchy.uxf -output=developers/images/object-hierarchy

news/images/x11-bridge.png: news/x11-bridge.uxf news/images
	umlet -action=convert -format=png -filename=news/x11-bridge.uxf -output=news/images/x11-bridge

news/images/virtualbox.png: news/virtualbox.uxf news/images
	umlet -action=convert -format=png -filename=news/virtualbox.uxf -output=news/images/virtualbox

news/images/wayland.png: news/wayland.uxf news/images
	umlet -action=convert -format=png -filename=news/wayland.uxf -output=news/images/wayland

sphynx:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) . $(BUILDDIR)/html

copy-images:
	cp images/* _build/html/_images/

html: subuser-standard/permissions-dot-json-file-format.rst command-docs pylint community.rst developers/contributing.rst developers/images/object-hierarchy.png news/images/x11-bridge.png  news/images/virtualbox.png news/images/wayland.png sphynx copy-images
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

release: html
	rm _build/html/_static/images/subuser-vision.mp4
	rm _build/html/_static/images/subuser-dev-freecad.mp4

deploy:
	./deploy.sh

clean:
	rm -rf _build/
