VERSION = $(shell cat VERSION)

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
