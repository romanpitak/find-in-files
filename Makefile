
.PHONY: home-install clean

build/fif: src/findinfiles.py
	mkdir --parents -- build
	printf '%s\n\n' '#!/usr/bin/env python3' > $@
	cat $< >> $@
	chmod a+x $@

home-install: build/fif
	cp $< ~/bin/fif

clean:
	rm --recursive --force -- build
