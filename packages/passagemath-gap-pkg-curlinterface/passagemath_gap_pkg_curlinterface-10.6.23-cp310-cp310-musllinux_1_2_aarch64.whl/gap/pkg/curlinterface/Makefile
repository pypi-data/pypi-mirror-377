#
# Makefile rules for the curlInterface package
#
KEXT_NAME = curl
KEXT_SOURCES = src/curl.c

KEXT_CFLAGS =  -I/host/sage-musllinux_1_2_aarch64/include -Igen
KEXT_LDFLAGS = -L/host/sage-musllinux_1_2_aarch64/lib -lcurl

KEXT_USE_AUTOCONF = 1

# include shared GAP package build system
GAPPATH = /host/sage-musllinux_1_2_aarch64/lib/gap
include Makefile.gappkg

# ensure pkgconfig.h is built
$(KEXT_OBJS): gen/pkgconfig.h
