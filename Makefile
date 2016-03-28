VERSION = $(shell cat VERSION)

packages: clean
	python3 setup.py bdist_wheel
	git archive --format=tar $(VERSION) > dist/subuser-$(VERSION).tar.gz
	cd dist ; gpg --detach-sign -a *.whl
	cd dist ; gpg --detach-sign -a *.tar.gz

deploy:
	twine upload dist/*.whl
	twine upload dist/*.whl.asc
	rsync -ru ./dist/ might@37.205.9.176:/home/might/web/subuser.org/rel/

clean:
	rm -r dist
	rm -r subuser.egg-info
	rm -r build
