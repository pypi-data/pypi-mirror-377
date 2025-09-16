#############################################################################
##
##  Global Variables
##
CC ?= gcc

BINDIR = bin/aarch64-unknown-linux-gnu-default64-kv9
GAPPATH = /host/sage-manylinux_2_28_aarch64/lib/gap/

CFLAGS ?= -O2 -g -Wall

#############################################################################
##
##  Targets
##
all: $(BINDIR)/fplsa4

$(BINDIR)/fplsa4: src/fplsa4.c
	mkdir -p $(BINDIR)
	$(CC) -o $@ $(CPPFLAGS) $(CFLAGS) $(LDFLAGS) $<

clean:
	rm -f $(BINDIR)/fplsa4

distclean: clean
	( cd doc; rm -f \
          manual.aux manual.bbl manual.blg manual.dvi manual.idl manual.idx \
          manual.ilg manual.ind manual.lab manual.log manual.pdf manual.six \
          manual.toc )


doc/manual.pdf htm/CHAP001.htm: doc/fplsa.tex doc/manual.tex
	cd doc && ./make_doc

doc: doc/manual.pdf htm/CHAP001.htm

Makefile: configure Makefile.in $(GAPPATH)/sysinfo.gap
	./configure $(GAPPATH)

.PHONY: all clean doc
