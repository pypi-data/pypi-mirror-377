#
# Makefile rules for the curlInterface package
#
KEXT_NAME = curl
KEXT_SOURCES = src/curl.c

KEXT_CFLAGS =  -I/host/sage-manylinux_2_28_x86_64/include -Igen
KEXT_LDFLAGS = -L/host/sage-manylinux_2_28_x86_64/lib -lcurl

KEXT_USE_AUTOCONF = 1

# include shared GAP package build system
GAPPATH = /host/sage-manylinux_2_28_x86_64/lib/gap
include Makefile.gappkg

# ensure pkgconfig.h is built
$(KEXT_OBJS): gen/pkgconfig.h
