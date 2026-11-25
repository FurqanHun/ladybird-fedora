%global debug_package %{nil}
%global tag 2026.47.8
# Commit: 0be55a57cc07ed258362c631a13a10bb4f6d707a
%global toolchain clang
%global _lto_cflags %{nil}
%define _build_id_links none
%define _find_debuginfo_dwz_opts %{nil}
%define _binary_payload w9T0.xzdio
%global __provides_exclude_from ^%{_libdir}/.*$
%global __requires_exclude ^(libav.*-ladybird|libswresample-ladybird|libicu.*|libdwarf).*$

Name:           ladybird
Version:        %{tag}
Release:        1%{?dist}
Summary:        A truly independent web browser with a novel engine
License:        BSD-2-Clause
URL:            https://ladybird.org/
Source0:        https://github.com/LadybirdBrowser/ladybird/archive/refs/tags/%{tag}.tar.gz#/%{name}-%{tag}.tar.gz

BuildRequires:  clang
BuildRequires:  compiler-rt
BuildRequires:  lld
BuildRequires:  llvm
BuildRequires:  gcc-c++
BuildRequires:  libstdc++-devel
BuildRequires:  rust >= 1.98.0
BuildRequires:  cargo
BuildRequires:  cmake >= 3.30
BuildRequires:  ninja-build
BuildRequires:  autoconf
BuildRequires:  autoconf-archive
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  nasm
BuildRequires:  ncurses-devel
BuildRequires:  patchelf
BuildRequires:  procps-ng
BuildRequires:  python3
BuildRequires:  perl-FindBin
BuildRequires:  perl-IPC-Cmd
BuildRequires:  perl-lib
BuildRequires:  perl-Time-Piece
BuildRequires:  git-core
BuildRequires:  curl
BuildRequires:  tar
BuildRequires:  unzip
BuildRequires:  zip
BuildRequires:  zlib-ng-compat-static
BuildRequires:  glslang
BuildRequires:  libdrm-devel
BuildRequires:  libglvnd-devel
BuildRequires:  libavcodec-free
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  xcb-util-wm-devel
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtpositioning-devel
BuildRequires:  qt6-qttools-devel
BuildRequires:  qt6-qtwayland-devel
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

Requires:       liberation-mono-fonts
Requires:       liberation-sans-fonts
Requires:       liberation-serif-fonts
Recommends:     libavcodec-free

%description
[ALPHA/PRE-RELEASE BUILD — DO NOT USE AS DAILY DRIVER]

Ladybird is a truly independent web browser with a novel engine built
from scratch based on web standards.

This package is built from official release tag %{tag}.

%prep
%autosetup -p1 -n %{name}-%{tag}

# Backport upstream commit 349b655 to find Rust FFI headers under Cargo 1.100+ layout
sed -i 's|"${CARGO_BUILD_SCRIPT_DIR}/${CRATE_NAME}-\*/root-output"|"${CARGO_BUILD_SCRIPT_DIR}/${CRATE_NAME}-*/root-output"\n    "${CARGO_BUILD_SCRIPT_DIR}/${CRATE_NAME}/*/run/root-output"|' Meta/CMake/sync_rust_ffi_header.cmake

%build
# Clear conflicting distribution flags that break vcpkg internal ports
unset CFLAGS
unset CXXFLAGS
unset LDFLAGS

export CC=clang
export CXX=clang++
export LADYBIRD_SOURCE_DIR=$(pwd)

# Pre-fetch crates required by LibJS and LibWasm
cargo fetch --locked --manifest-path Cargo.toml
cargo fetch --locked --manifest-path Libraries/LibJS/Flap/Cargo.toml

# Bootstrap vcpkg toolchain for the Distribution preset
python3 ./Meta/ladybird.py vcpkg --preset Distribution

cmake --preset Distribution -B Build \
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DLADYBIRD_VERSION=%{version} \
    -DLADYBIRD_BASELINE_CPU_TARGET=ON \
    -DENABLE_INSTALL_FREEDESKTOP_FILES=ON \
    -DENABLE_INSTALL_HEADERS=OFF \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
    -DCMAKE_INSTALL_LIBEXECDIR=libexec \
    -DCMAKE_EXE_LINKER_FLAGS="-Wl,--exclude-libs,ALL" || {
        echo "=== CMAKE / VCPKG INSTALL FAILED ==="
        for f in $(ls -t Build/vcpkg-distribution/buildtrees/*/*-err.log 2>/dev/null | head -n 5); do
            echo "=== ERROR LOG: $f ==="
            cat "$f"
        done
        for f in $(ls -t Build/vcpkg-distribution/buildtrees/*/*-out.log 2>/dev/null | head -n 5); do
            echo "=== OUT LOG: $f ==="
            tail -n 80 "$f"
        done
        exit 1
    }

cmake --build Build -j%{?_smp_build_ncpus}

%install
DESTDIR=%{buildroot} cmake --install Build

# Create lowercase symlink for convenience
ln -sf Ladybird %{buildroot}%{_bindir}/ladybird

# Remove standalone developer test utilities not needed in browser package
rm -f %{buildroot}%{_bindir}/js
rm -f %{buildroot}%{_bindir}/wasm

# Remove development cmake files if installed
rm -rf %{buildroot}%{_datadir}/Ladybird
rm -f %{buildroot}%{_datadir}/Lagom/*.cmake

# Clean up static libraries and stray COMMIT file not needed in binary package
rm -f %{buildroot}%{_libdir}/*.a
rm -f %{buildroot}%{_prefix}/COMMIT

# Remove duplicate shared libraries already provided by Fedora base packages
rm -f %{buildroot}%{_libdir}/libdbus-1.so*
rm -f %{buildroot}%{_libdir}/libunistring.so*
rm -f %{buildroot}%{_libdir}/libidn2.so*

# Keep symbol tables for readable crash backtraces in pre-alpha; uncomment to strip:
# find %{buildroot}%{_bindir} %{buildroot}%{_libexecdir} -type f -exec strip --strip-all {} + 2>/dev/null || :

desktop-file-validate %{buildroot}%{_datadir}/applications/org.ladybird.Ladybird.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/org.ladybird.Ladybird.metainfo.xml

%files
%license LICENSE
%doc README.md
%{_bindir}/*
%{_libexecdir}/*
%{_libdir}/*
%{_datadir}/Lagom/
%{_datadir}/applications/org.ladybird.Ladybird.desktop
%{_datadir}/icons/hicolor/*/apps/org.ladybird.Ladybird.*
%{_datadir}/dbus-1/services/org.ladybird.Ladybird.service
%{_datadir}/metainfo/org.ladybird.Ladybird.metainfo.xml

%changelog
* Wed Nov 25 2026 FurqanHun <furqanhun@proton.me> - 2026.47.8-1
- Update to release tag 2026.47.8

* Tue Nov 24 2026 FurqanHun <furqanhun@proton.me> - 2026.47.7-3
- Remove duplicate system libraries (libdbus-1, libunistring, libidn2) to prevent RPM file conflicts

* Tue Nov 24 2026 FurqanHun <furqanhun@proton.me> - 2026.47.7-2
- Filter bundled libraries from Requires to resolve DNF install dependency errors

* Mon Nov 23 2026 FurqanHun <furqanhun@proton.me> - 2026.47.7-1
- Update to official First Alpha release tag 2026.47.7
- Backport upstream commit 349b655 for Cargo 1.100+ FFI header path layout
- Switch from qt6-qtbase-private-devel to public qt6-qtbase-devel
- Include bundled dynamic runtime libraries in libdir
- Update baseline CPU target flag to LADYBIRD_BASELINE_CPU_TARGET

* Tue Nov 17 2026 FurqanHun <furqanhun@proton.me> - 2026.47.1-1
- Update to official release tag 2026.47.1

* Mon Nov 16 2026 FurqanHun <furqanhun@proton.me> - 2026.46.2-3
- Remove standalone developer js and wasm test runners
- Clean up unused Lagom development cmake files from assets directory
- Use xz -9 payload compression matching upstream CPack release archive

* Sun Nov 15 2026 FurqanHun <furqanhun@proton.me> - 2026.46.2-2
- Hide static archive symbols with --exclude-libs,ALL to fix Fontconfig collision with Qt plugins
- Fix CMAKE_INSTALL_LIBEXECDIR to relative 'libexec' so Hub helper is located correctly
- Disable debug_package to speed up build and packaging

* Sun Nov 15 2026 FurqanHun <furqanhun@proton.me> - 2026.46.2-1
- Update to official release tag 2026.46.2
- Switch to Clang toolchain and Distribution preset
- Remove legacy skia patches (handled automatically via vcpkg overlay)

* Sat Mar 14 2026 FurqanHun - 0.1.0-3.20260314git19af2be
- fixing build?

* Sat Mar 14 2026 FurqanHun - 0.1.0-2.20260314git19af2be
- Rebuild bump for Copr

* Sat Mar 14 2026 FurqanHun - 0.1.0-1.20260314git19af2be
- Clean rebuild following official Ladybird Fedora build docs
- vcpkg handles Skia and other deps, no cz-skia needed
- rust + cargo added for LibJS

* Wed Aug 06 2025 FurqanHun - 0.1.0-15.20250806git1201447
- patch fix???

* Wed Aug 06 2025 FurqanHun - 0.1.0-14.20250806git1201447
- patch fix

* Wed Aug 06 2025 FurqanHun - 0.1.0-13.20250806git1201447
- rm vcpkg, patch use-cz-skia...

* Wed Aug 06 2025 FurqanHun - 0.1.0-12.20250806git1201447
- vcpkg install

* Wed Aug 06 2025 FurqanHun - 0.1.0-11.20250806git1201447
- cmnt cz-skia-devel syslink + trying vcpkg

* Wed Aug 06 2025 FurqanHun - 0.1.0-10.20250806git1201447
- cz-skia-devel syslink

* Tue Aug 05 2025 FurqanHun - 0.1.0-9.20250806git1201447
- BuildRequires: openjpeg-devel and BuildRequires: cz-skia-devel (copr)

* Tue Aug 05 2025 FurqanHun - 0.1.0-8.20250806git1201447
- Add final configuration dependency: fontconfig-devel
- if it works i'll sleep

* Tue Aug 05 2025 FurqanHun - 0.1.0-7.20250806git1201447
- Add anohter fuuu missing dependency: libicu-devel
- Pls work im losing braincells

* Tue Aug 05 2025 FurqanHun - 0.1.0-6.20250806git1201447
- Add missing BuildRequires: openssl-devel
- Pls work

* Tue Aug 05 2025 FurqanHun - 0.1.0-5.20250805git1201447
- Add missing BuildRequires: libtommath-devel

* Tue Aug 05 2025 FurqanHun - 0.1.0-4.20250805git1201447
- Correct package name to fast_float-devel
- Pls work

* Tue Aug 05 2025 FurqanHun - 0.1.0-3.20250805git1201447
- Add missing BuildRequires: fastfloat-devel
- Pls work

* Tue Aug 05 2025 FurqanHun - 0.1.0-2.20250805git1201447
- Add missing BuildRequires: simdutf-devel
- omfg work

* Tue Aug 05 2025 FurqanHun - 0.1.0-1.20250805git1201447
- Pls work

* Thu Mar 13 2025 FurqanHun - 0.1-1
- Initial package