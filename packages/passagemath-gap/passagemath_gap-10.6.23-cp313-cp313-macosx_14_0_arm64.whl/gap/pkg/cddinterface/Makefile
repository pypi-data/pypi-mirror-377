#
# Makefile rules for the CddInterface package
#
KEXT_NAME = CddInterface
KEXT_SOURCES = src/CddInterface.cc

KEXT_CFLAGS = -DGMPRATIONAL -I/Users/runner/sage-local/include/cdd -I/Users/runner/sage-local/include/cddlib -I/Users/runner/sage-local/include
KEXT_LDFLAGS = -L/Users/runner/sage-local/lib -lcddgmp -lgmp

KEXT_USE_AUTOCONF = 1

# include shared GAP package build system
GAPPATH = /Users/runner/sage-local/lib/gap
include Makefile.gappkg
