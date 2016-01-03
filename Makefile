ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
TEMPDIR := $(shell mktemp -t tmp.XXXXXX -d)
FLAKE8 := $(shell which flake8)
PYLINT := $(shell which pylint3 || which pylint)
UNAME := $(shell uname)
DOCKERTAG = andrewferrier/cromer

determineversion:
	$(eval GITDESCRIBE := $(shell git describe --dirty))
	sed 's/Version: .*/Version: $(GITDESCRIBE)/' debian/DEBIAN/control_template > debian/DEBIAN/control

determineversion_brew:
	$(eval GITDESCRIBE := $(shell git describe --abbrev=0))
	sed 's/X\.Y/$(GITDESCRIBE)/' brew/cromer_template.rb > brew/cromer.rb

ifeq ($(UNAME),Linux)
builddeb: determineversion builddeb_real
else
builddeb: rundocker_getdebs
endif

builddeb_real:
	sudo apt-get install build-essential
	cp -R debian/DEBIAN/ $(TEMPDIR)
	mkdir -p $(TEMPDIR)/usr/bin
	mkdir -p $(TEMPDIR)/usr/share/doc/cromer
	cp cromer $(TEMPDIR)/usr/bin
	cp README* $(TEMPDIR)/usr/share/doc/cromer
	cp LICENSE* $(TEMPDIR)/usr/share/doc/cromer
	fakeroot chmod -R u=rwX,go=rX $(TEMPDIR)
	fakeroot chmod -R u+x $(TEMPDIR)/usr/bin
	fakeroot dpkg-deb --build $(TEMPDIR) .

makebrewlinks:
	ln -sf $(ROOT_DIR)/brew/cromer.rb /usr/local/Library/Formula

installbrew: makebrewlinks determineversion_brew
	brew install -f cromer

reinstallbrew: makebrewlinks determineversion_brew
	brew reinstall cromer

builddocker: determineversion
	docker build -t $(DOCKERTAG) .
	docker tag -f $(DOCKERTAG):latest $(DOCKERTAG):$(GITDESCRIBE)

rundocker_testing: builddocker
	docker run --rm -t $(DOCKERTAG) bash -c 'cd /tmp/cromer && make unittest && make analysis'

rundocker_getdebs: builddocker
	docker run --rm -v ${PWD}:/debs $(DOCKERTAG) sh -c 'cp /tmp/*.deb /debs'

analysis:
	# Debian version is badly packaged, make sure we are using Python 3.
	-/usr/bin/env python3 $(FLAKE8) --max-line-length=132 cromer tests/
	$(PYLINT) -r n --disable=line-too-long --disable=missing-docstring --disable=locally-disabled cromer tests/

unittest:
	python3 -m unittest discover

unittest_verbose:
	python3 -m unittest discover -f -v
