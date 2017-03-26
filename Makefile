VERSION = $(shell cat VERSION)
REPO_FILES ?= git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0

packages: clean
	python3 setup.py bdist_wheel
	git archive --format=tar.gz $(VERSION) > dist/subuser-$(VERSION).tar.gz
	cd dist ; gpg --detach-sign -a *.whl
	cd dist ; gpg --detach-sign -a *.tar.gz

deploy-subuser.org:
	rsync -ru ./dist/ might@37.205.9.176:/home/might/web/subuser.org/rel/

deploy-pypi:
	twine upload dist/*.whl
	twine upload dist/*.whl.asc

deploy: deploy-subuser.org deploy-pypi
	echo Deployed

clean:
	rm -r dist ; exit 0
	rm -r subuser.egg-info ; exit 0
	rm -r build ; exit 0

qa-https-everywhere:
	$(REPO_FILES) | xargs --null sed --regexp-extended --in-place 's#http(:\\?/\\?/)(momentjs\.com|overpass-turbo\.eu|www\.gnu\.org|stackoverflow\.com|(:?www\.)?openstreetmap\.(org|de)|nominatim\.openstreetmap\.org|taginfo\.openstreetmap\.org|wiki\.openstreetmap\.org|josm.openstreetmap.de|www.openstreetmap.org\\/copyright|github\.com|xkcd\.com|www\.heise\.de|www\.readthedocs\.org|askubuntu\.com|xpra\.org|docker\.com|linuxcontainers\.org|www\.ecma-international\.org|www\.w3\.org|example\.com|www\.example\.com)#https\1\2#g;'
	$(REPO_FILES) | xargs --null sed -i 's#http://overpass-api\.de#https://overpass-api.de#g;'
	$(REPO_FILES) | xargs --null sed --regexp-extended --in-place 's#http://(\w+\.wikipedia\.org)#https://\1#g;'
