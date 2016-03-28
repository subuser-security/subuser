VERSION = $(shell cat VERSION)

packages:
	python3 setup.py bdist_wheel
	git archive --format=tar $(VERSION) > dist/subuser-$(VERSION).tar.gz
	cd dist ; gpg --detach-sign -a *.whl
	cd dist ; gpg --detach-sign -a *.tar.gz

deploy:
	twine upload dist/*
	scp rsync -ru ./dist/ might@37.205.9.176:/home/might/web/subuser.org/rel/
	rm -r dist
