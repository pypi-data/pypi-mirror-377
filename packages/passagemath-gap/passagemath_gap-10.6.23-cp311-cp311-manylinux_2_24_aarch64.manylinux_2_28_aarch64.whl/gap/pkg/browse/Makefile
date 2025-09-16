# makefile prototype for the Browse package                    Frank Lübeck

GAPPATH=/host/sage-manylinux_2_28_aarch64/lib/gap/
include $(GAPPATH)/sysinfo.gap

GAPINCL=-I$(GAPPATH)/src -I$(GAPPATH)/bin/$(GAParch)

PKGROOT=$(shell pwd)

LOPTS=$(LDFLAGS) -lpanel -lncurses

.PHONY: manual clean distclean doc docclean WIDECHARS

bin/$(GAParch)/ncurses.so: src/ncurses.c Makefile
	mkdir -p bin/$(GAParch)
	$(GAC) -p "$(CFLAGS)" -d -o \
	     bin/$(GAParch)/ncurses.so src/ncurses.c -L "${LOPTS}"

# just make it again when called with 'manual'
##  manual: doc/manual.six
##  doc/manual.six: doc/main.xml doc/browsebib.xml doc/appl.xml doc/browse.xml \
##                  doc/curses.xml doc/intro.xml doc/util.xml
manual:
	($(GAP) -l "../../;" -r < makedocrel.g)
	echo "LaTeX warnings:"
	grep "\(^LaTeX Warning\|^Overfull \\hbox\)" doc/main.log; exit 0

# for compatibility with other packages
clean:
	rm -rf bin/$(GAParch) *~
# clean last build
cleanlast:
	rm -rf bin/$(GAParch) Makefile *~
# clean all builds
distclean:
	rm -rf bin/* Makefile Makefile-*

doc:
	($(GAP)  < makedocrel.g)

docclean:
	(cd  doc; ./clean)

test:
	$(GAP) -b -q -r  tst/test.tst

# experimental so far
WIDECHARS:
	$(GAC) -p "$(CFLAGS)" -d -o bin/$(GAParch)/ncurses.so \
        src/ncurses.c -p -DWIDECHARS -L "-lpanelw  -lncursesw"

