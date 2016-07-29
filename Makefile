
.PHONY: home-install clean

build/fif: src/findinfiles.py
	mkdir build
	printf '%s\n\n' '#!/bin/env python3' > $@
	cat $< >> $@
	chmod a+x $@

home-install: build/fif
	cp $< ~/bin/fif

clean:
	rm --recursive --force -- build
