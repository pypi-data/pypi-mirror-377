#
# Makefile rules for the curlInterface package
#
KEXT_NAME = curl
KEXT_SOURCES = src/curl.c

KEXT_CFLAGS =  -I/usr/local/Cellar/curl/8.15.0/include -Igen
KEXT_LDFLAGS = -L/usr/local/Cellar/curl/8.15.0/lib -lcurl

KEXT_USE_AUTOCONF = 1

# include shared GAP package build system
GAPPATH = /Users/runner/sage-local/lib/gap
include Makefile.gappkg

# ensure pkgconfig.h is built
$(KEXT_OBJS): gen/pkgconfig.h
