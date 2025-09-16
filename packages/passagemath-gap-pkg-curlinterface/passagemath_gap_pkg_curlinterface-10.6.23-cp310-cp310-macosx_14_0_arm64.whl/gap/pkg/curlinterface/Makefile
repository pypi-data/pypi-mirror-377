#
# Makefile rules for the curlInterface package
#
KEXT_NAME = curl
KEXT_SOURCES = src/curl.c

KEXT_CFLAGS =  -Igen
KEXT_LDFLAGS = -lcurl

KEXT_USE_AUTOCONF = 1

# include shared GAP package build system
GAPPATH = /Users/runner/sage-local/lib/gap
include Makefile.gappkg

# ensure pkgconfig.h is built
$(KEXT_OBJS): gen/pkgconfig.h
