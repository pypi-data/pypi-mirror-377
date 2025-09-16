#
# Makefile rules for the CddInterface package
#
KEXT_NAME = CddInterface
KEXT_SOURCES = src/CddInterface.cc

KEXT_CFLAGS = -DGMPRATIONAL -I/host/sage-manylinux_2_28_aarch64/include/cdd -I/host/sage-manylinux_2_28_aarch64/include/cddlib -I/host/sage-manylinux_2_28_aarch64/include
KEXT_LDFLAGS = -L/host/sage-manylinux_2_28_aarch64/lib -lcddgmp -lgmp

KEXT_USE_AUTOCONF = 1

# include shared GAP package build system
GAPPATH = /host/sage-manylinux_2_28_aarch64/lib/gap
include Makefile.gappkg
