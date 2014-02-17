# avoid dpkg-dev dependency; fish out the version with sed
VERSION := $(shell sed 's/.*(\(.*\)).*/\1/; q' debian/changelog)

MAKEDEV := /sbin/MAKEDEV

ifeq ($(shell uname),Linux)
all: devices.tar.gz
else
all:
endif

clean:
	rm -f devices.tar.gz
	rm -rf dev

DSDIR=$(DESTDIR)/usr/share/debootstrap
install:
	mkdir -p $(DSDIR)/scripts
	mkdir -p $(DESTDIR)/usr/sbin

	cp -a scripts/* $(DSDIR)/scripts/
	install -o root -g root -m 0644 functions $(DSDIR)/

	sed 's/@VERSION@/$(VERSION)/g' debootstrap >$(DESTDIR)/usr/sbin/debootstrap
	chown root:root $(DESTDIR)/usr/sbin/debootstrap
	chmod 0755 $(DESTDIR)/usr/sbin/debootstrap

ifeq ($(shell uname),Linux)
	install -o root -g root -m 0644 devices.tar.gz $(DSDIR)/
endif

devices.tar.gz:
	rm -rf dev
	mkdir -p dev
	chown 0:0 dev
	chmod 755 dev
	(cd dev && $(MAKEDEV) std ptmx fd consoleonly)
	tar cf - dev | gzip -9 >devices.tar.gz
	@if [ "$$(tar tvf devices.tar.gz | wc -l)" -lt 2 ]; then \
		echo " ** devices.tar.gz is empty!" >&2; \
		exit 1; \
	fi
	rm -rf dev
