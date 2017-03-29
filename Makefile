TOPDIR:=$(shell pwd)/topdir
BUILD_DIR := $(shell pwd)/.blddir
SRCROOT := $(shell pwd)

NAME:=ilorest
VERSION:=1.9.0
RELEASE:=1
SPHINXBUILD:=$(BUILD_DIR)/pylib/Sphinx-1.0.7/sphinx-build.py

CREATE_CHROOT := <USERS MUST CHANGE THESE SETTINGS TO ADAPT TO THEIR ENVI>
CHROOT := <USERS MUST CHANGE THESE SETTINGS TO ADAPT TO THEIR ENVI>

ifdef MTX_PRODUCT_VERSION
  VERSION:=$(MTX_PRODUCT_VERSION)
endif


ifdef MTX_BUILD_NUMBER
  RELEASE:=$(MTX_BUILD_NUMBER)
endif


all: rpm

export PYTHONPATH=$(BUILD_DIR)/pylib/docutils-0.8:$(BUILD_DIR)/pylib/roman-2.0.0/src:$(BUILD_DIR)/pylib/Jinja2-2.5.5:$(BUILD_DIR)/pylib/Sphinx-1.0.7
export http_proxy=proxy.houston.hp.com:8080
tbz:
	rm -rf $(BUILD_DIR)/pylib
	mkdir -p $(BUILD_DIR)/pylib
	cd $(BUILD_DIR)/pylib && unzip $(SRCROOT)/packaging/packages/roman/roman-2.0.0.zip
	tar xfz $(SRCROOT)/packaging/packages/sphinx/Sphinx-1.0.7.tar.gz -C $(BUILD_DIR)/pylib
	tar xfz $(SRCROOT)/packaging/packages/docutils/docutils-0.8.tar.gz -C $(BUILD_DIR)/pylib
	tar xfz $(SRCROOT)/packaging/packages/jinja/Jinja2-2.5.5.tar.gz -C $(BUILD_DIR)/pylib

	rm -rf "$(NAME)-$(VERSION)"
	rm -f  "$(NAME)-$(VERSION).tar.bz2"
	mkdir -p "$(NAME)-$(VERSION)"
	tar --exclude=$(NAME)-$(VERSION) \
            --exclude=.svn --exclude=*.pyc --exclude=rdmc-pyinstaller*.spec --exclude=./Makefile -cf - * |\
            ( tar -C $(NAME)-$(VERSION) -xf -)
	sed -e "s/\%VERSION\%/$(VERSION)/g"  -e "s/\%RELEASE\%/$(RELEASE)/g"\
            rdmc.spec.in > "$(NAME)-$(VERSION)/rdmc.spec"
	sed -i -e "s/\%VERSION\%/$(VERSION)/g" -e "s/\%RELEASE\%/$(RELEASE)/g" \
            docs/sphinx/conf.py

	make -C "$(NAME)-$(VERSION)/docs/sphinx" man  SPHINXBUILD=$(SPHINXBUILD)
	gzip -c "$(NAME)-$(VERSION)/docs/sphinx/_build/man/ilorest.8" > "$(NAME)-$(VERSION)/docs/sphinx/_build/man/ilorest.8.gz"

	rm -rf "$(NAME)-$(VERSION)/Sphinx-1.0.7"
	rm -rf "$(NAME)-$(VERSION)/docutils-0.8"
	rm -rf "$(NAME)-$(VERSION)/Jinja2-2.5.5"
	rm -rf "$(NAME)-$(VERSION)/scexe_src/scexe.spec"
	cp -r $(MTX_STAGING_PATH)/schemas "$(NAME)-$(VERSION)"
	cp -r $(MTX_STAGING_PATH)/externals "$(NAME)-$(VERSION)"
	tar cfj "$(NAME)-$(VERSION).tar.bz2" "$(NAME)-$(VERSION)"
	rm -rf "$(NAME)-$(VERSION)"

rpmprep:
	rm -rf $(TOPDIR)
	mkdir -p $(TOPDIR)
	cd $(TOPDIR) && mkdir -p BUILD RPMS SOURCES SPECS SRPMS

rdmc.spec: rdmc.spec.in
	sed -e "s/\%VERSION\%/$(VERSION)/g" -e "s/\%RELEASE\%/$(RELEASE)/g" \
	   $< > $(TOPDIR)/SPECS/$@

rpm: rpmprep tbz rdmc.spec
	cp "$(NAME)-$(VERSION).tar.bz2" $(TOPDIR)/SOURCES/
	rpmbuild -ba --define '_topdir $(TOPDIR)' $(TOPDIR)/SPECS/rdmc.spec

clean:
	rm -f "$(NAME)-$(VERSION).tar.bz2"
	rm -rf topdir .blddir


DEBCHROOTD := $(BUILD_DIR)/chroots/squeeze

rpm-freeze: freeze-src tbz rpms

rpms:
	$(call freeze-chroot,x86_64)
	$(CHROOT) $(DEBCHROOTD) yum install -y which

	$(CHROOT) $(DEBCHROOTD) bash -c 'adduser monkey'
	cp "$(NAME)-$(VERSION).tar.bz2" $(DEBCHROOTD)/home/monkey
	$(CHROOT) $(DEBCHROOTD) bash -c 'su - monkey -c "mkdir -p ~/build && cd ~/build && mkdir -p BUILD RPMS SOURCES SPECS SRPMS"'
	echo "rpmbuild -ta --define '_topdir /home/monkey/build/' /home/monkey/$(NAME)-$(VERSION).tar.bz2 " > $(DEBCHROOTD)/home/monkey/c.sh
	$(CHROOT) $(DEBCHROOTD) bash -c 'chmod a+x /home/monkey/c.sh'
	$(CHROOT) $(DEBCHROOTD) bash -c 'su - monkey -c "/home/monkey/c.sh"'
	cp -r $(DEBCHROOTD)/home/monkey/build/RPMS/ .

	-find ./RPMS -type f -name '*-debuginfo-*.rpm' -exec rm -f {} \;
	-find ./RPMS -type d -empty -exec rmdir {} \;

ifdef MTX_COLLECTION_PATH
	cp -r ./RPMS $(MTX_COLLECTION_PATH)/
	find $(MTX_COLLECTION_PATH) -type f -name '*.rpm' -exec hpsign --signonly {} \;
endif


freeze-src:
	rm -rf hp


define freeze-bin
	$(call freeze-src,$1)

	$(CHROOT) $1 bash -c 'cd /$(NAME)-$(VERSION) && /opt/python2.7/bin/python2.7 setup.py build'

	bash ./scexe_src/scexe -o $(NAME) -i $(NAME) $1/$(NAME)-$(VERSION)/build/exe.linux-x86_64*/*
endef

define freeze-chroot
	rm -rf $(BUILD_DIR)/chroots
# create the chroot
	$(CREATE_CHROOT) -d RHEL6.7 -a $1 -D $(DEBCHROOTD)

	$(CHROOT) $(DEBCHROOTD) yum install -y zlib-devel
	$(CHROOT) $(DEBCHROOTD) yum install -y libxml2-devel libxslt-devel ncurses-devel openssl-devel expat-devel sqlite-devel readline-devel bzip2-devel db4-devel

	tar xfz $(SRCROOT)/packaging/python/Python-2.7.11.tgz -C $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /Python-2.7.11 && ./configure --prefix=/opt/python2.7 --enable-shared'
	$(CHROOT) $(DEBCHROOTD) make -C /Python-2.7.11
	$(CHROOT) $(DEBCHROOTD) make -C /Python-2.7.11 altinstall
	echo "/opt/python2.7/lib" >> $(DEBCHROOTD)/etc/ld.so.conf.d/opt-python2.7.conf
	$(CHROOT) $(DEBCHROOTD) ldconfig

	#Added external packages
	tar xfz $(SRCROOT)/packaging/ext/setuptools-2.2.tar.gz -C $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /setuptools-2.2 && /opt/python2.7/bin/python2.7 setup.py install'

	unzip $(SRCROOT)/packaging/ext/distribute-0.7.3.zip -d $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /distribute-0.7.3 && /opt/python2.7/bin/python2.7 setup.py install'

	tar xfz $(SRCROOT)/packaging/pyinstaller/PyInstaller-3.1.1.tar.gz -C $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /PyInstaller-3.1.1 && /opt/python2.7/bin/python2.7 setup.py install'

	tar xfj $(SRCROOT)/packaging/ext/upx-3.91-$1_linux.tar.bz2 -C $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /upx-3.91-$1_linux && cp upx /bin'

	tar xfz $(SRCROOT)/packaging/ext/jsonpointer-1.1.tar.gz -C $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /jsonpointer-1.1 && /opt/python2.7/bin/python2.7 setup.py install'

	tar xfz $(SRCROOT)/packaging/ext/six-1.7.2.tar.gz -C $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /six-1.7.2 && /opt/python2.7/bin/python2.7 setup.py install'

	tar xfz $(SRCROOT)/packaging/ext/ply-3.4.tar.gz -C $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /ply-3.4 && /opt/python2.7/bin/python2.7 setup.py install'

	tar xfz $(SRCROOT)/packaging/ext/decorator-3.4.0.tar.gz -C $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /decorator-3.4.0 && /opt/python2.7/bin/python2.7 setup.py install'

	tar xfz $(SRCROOT)/packaging/ext/jsonpatch-1.3.tar.gz -C $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /jsonpatch-1.3 && /opt/python2.7/bin/python2.7 setup.py install'

	tar xfz $(SRCROOT)/packaging/ext/jsonpath-rw-1.3.0.tar.gz -C $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /jsonpath-rw-1.3.0 && /opt/python2.7/bin/python2.7 setup.py install'

	tar xfz $(SRCROOT)/packaging/ext/recordtype-1.1.tar.gz -C $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /recordtype-1.1 && /opt/python2.7/bin/python2.7 setup.py install'

	tar xfz $(SRCROOT)/packaging/ext/urlparse2-1.1.1.tar.gz -C $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /urlparse2-1.1.1 && /opt/python2.7/bin/python2.7 setup.py install'

	tar xfz $(SRCROOT)/packaging/ext/readline-6.2.4.1.tar.gz -C $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /readline-6.2.4.1 && /opt/python2.7/bin/python2.7 setup.py install'

	tar xfz $(SRCROOT)/packaging/ext/setproctitle-1.1.8.tar.gz -C $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /setproctitle-1.1.8 && /opt/python2.7/bin/python2.7 setup.py install'

	tar xfz $(SRCROOT)/packaging/ext/validictory-1.0.1.tar.gz -C $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /validictory-1.0.1 && /opt/python2.7/bin/python2.7 setup.py install'

	tar xfz $(SRCROOT)/packaging/ext/pyudev-0.21.0.tar.gz -C $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /pyudev-0.21.0 && /opt/python2.7/bin/python2.7 setup.py install'

	cp -r $(MTX_STAGING_PATH)/externals/*.zip packaging/ext
	unzip packaging/ext/python-ilorest-library-1.9.0.zip -d $(DEBCHROOTD)
	$(CHROOT) $(DEBCHROOTD) bash -c 'cd /python-ilorest-library-1.9.0 && /opt/python2.7/bin/python2.7 setup.py install'
endef

freeze: freeze-x86_64

freeze-x86_64:
	$(call freeze-chroot,x86_64)
	$(call freeze-bin,$(DEBCHROOTD))

ifdef MTX_COLLECTION_PATH
	mkdir -p ${MTX_COLLECTION_PATH}/x86_64
	mv ./$(NAME) ${MTX_COLLECTION_PATH}/x86_64
endif

freeze-i386:
	$(call freeze-chroot,i386)
	$(call freeze-bin,$(DEBCHROOTD),i386)

ifdef MTX_COLLECTION_PATH
	mkdir -p ${MTX_COLLECTION_PATH}/i386
	mv ./$(NAME) ${MTX_COLLECTION_PATH}/i386
endif

deb:
	sudo apt-get -y install alien
	sudo alien $(MTX_STAGING_PATH)/rpmlocation/RPMS/x86_64/*.rpm
	mkdir temp
	dpkg-deb -R *.deb temp
	mv temp/usr/lib64 temp/usr/lib
	mkdir temp/usr/lib/x86_64-linux-gnu
	cp temp/usr/lib/ilorest_chif.so temp/usr/lib/x86_64-linux-gnu/
	rm temp/usr/lib/ilorest_chif.so
	dpkg-deb -b temp new.deb
	rm ilorest*.deb
	mv new.deb $(NAME)-$(VERSION)-$(RELEASE).x86_64.deb
	mkdir -p DEB && cp *.deb DEB
	cp -r DEB $(MTX_COLLECTION_PATH)/
