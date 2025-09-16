# sample makefile
CC?=cc
GAPPATH=/host/sage-musllinux_1_2_x86_64/lib/gap/

all:
	@mkdir -p bin/x86_64-pc-linux-musl-default64-kv9
	cd src && make
	@cp src/ace bin/x86_64-pc-linux-musl-default64-kv9/ace

clean:	
	rm -rf bin src/ace

distclean: clean
	rm -rf Makefile htm

# use this target only if you want to build the manual from scratch.
doc:
	(cd doc;./make_doc)

otherdoc:
	(cd standalone-doc;latex ace3001;bibtex ace3001;latex ace3001;latex ace3001)
	(cd standalone-doc;dvips ace3001 -o)
	(cd standalone-doc;rm ace3001.{toc,blg,log,aux})

Makefile: configure Makefile.in $(GAPPATH)/sysinfo.gap
	./configure "$(GAPPATH)"

.PHONY: all clean distclean doc otherdoc
