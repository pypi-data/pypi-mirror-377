#
# Makefile rules for the NormalizInterface package
#
KEXT_NAME = NormalizInterface
KEXT_SOURCES = src/normaliz.cc

# Normaliz requires C++11; but some of its dependencies (well at least
# e-Antic) requires C++14. Since that's been in compilers for a decade
# now, just always request C++14 support. Note: we use gnu++14 instead
# of std++14 only for compatibility with GAP versions before 4.12 on
# Cygwin, see <https://github.com/gap-packages/NormalizInterface/pull/91>.
KEXT_CXXFLAGS =  -I/host/sage-manylinux_2_28_aarch64/var/tmp/sage/build/gap_packages-4.14.0.p0/src/pkg/normalizinterface/NormalizInstallDir/include   -std=gnu++14
KEXT_LDFLAGS = -Wl,-rpath-link,/host/sage-manylinux_2_28_aarch64/lib -L/host/sage-manylinux_2_28_aarch64/lib -Wl,-rpath,/host/sage-manylinux_2_28_aarch64/lib -Wl,-rpath-link,/host/sage-manylinux_2_28_aarch64/lib -L/host/sage-manylinux_2_28_aarch64/lib -Wl,-rpath,/host/sage-manylinux_2_28_aarch64/lib   -lgmp -Wl,-rpath,/host/sage-manylinux_2_28_aarch64/var/tmp/sage/build/gap_packages-4.14.0.p0/src/pkg/normalizinterface/NormalizInstallDir/lib -L/host/sage-manylinux_2_28_aarch64/var/tmp/sage/build/gap_packages-4.14.0.p0/src/pkg/normalizinterface/NormalizInstallDir/lib -lnormaliz -lstdc++

KEXT_USE_AUTOCONF = 1

# include shared GAP package build system
GAPPATH = /host/sage-manylinux_2_28_aarch64/lib/gap
include Makefile.gappkg
