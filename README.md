# Ladybird for Fedora

This repo got the recipe to build Ladybird on Fedora. The spec file uses official CalVer release tags and sticks as closely as possible to upstream's official Distribution CMake preset, only adding what's needed for Fedora packaging.

> [!WARNING]
> Ladybird is an alpha browser. DON'T USE IT FOR DAILY DRIVING OR BANKING OR ANYTHING IMPORTANT. It doesn't even have all the basic web security features yet.


---

## Installation

### Official Upstream Repository (Recommended)

As of Alpha 1 (`2026.47.7`), Ladybird provides official signed RPM repositories for Fedora 44 and 45:

```sh
sudo dnf config-manager addrepo --from-repofile='https://rpm.ladybird.org/ladybird.repo'
sudo dnf install ladybird
```

Upstream packages install as a self-contained bundle into `/opt/ladybird`.

### Community Copr

If you are on Fedora 43, or prefer a native packaging layout (`/usr/bin`, `/usr/libexec`, `/usr/lib64`, `/usr/share`) with unstripped symbol tables for readable backtraces, you can use the Copr package built from this spec (occasionally updated as time permits):

```sh
sudo dnf copr enable furqanhun/ladybird-test
sudo dnf install ladybird
```

---

## Why Rawhide is Not Supported (Yet)

There are two main reasons:

First is rust and `-Dwarnings`. upstream ladybird passes `-Dwarnings` to `rustc` by default in their cmake files (`Meta/CMake/rust_crate.cmake`). Rawhide ships the newest compiler versions, and whenever a new rust release deprecates an api, rustc throws a warning. even though the code works completely fine, `-Dwarnings` treats any warning as a hard error and kills the build. we can patch this pretty easily by passing `-Adeprecated` so it ignores deprecation warnings, but it's cleaner to wait for upstream to relax it.

The second thing was cargo 1.100. cargo dropped an internal cache file called `root-output`, which cmake (`Meta/CMake/sync_rust_ffi_header.cmake`) was expecting to find `RustFFI.h`. upstream actually fixed this on master (commit `349b655`), but didn't cherry-pick it into the `2026.47.7` alpha tag. and since fedora pushed cargo 1.100 to fedora 43, 44, and 45 as well, I just backported that cmake fix in `%prep` so the build doesn't crash on cargo.

So until upstream adds a way to relax `-Dwarnings` for distro builds (or I decide to patch in `-Adeprecated`), rawhide builds will stay paused (for now atleast). Fedora 43, 44, and 45 work fine.

---

## Alpha Warning & Security

Once again, Ladybird is an alpha browser that is still early in development.

Do not use this as your daily driver, and definitely do not use it for banking, personal email, passwords, or anything sensitive.

Building a browser engine from scratch is a massive task and web security is brutal. Ladybird does not have complete multi-process sandboxing, mature site isolation, or years of battle-tested exploit mitigations yet. Running arbitrary web code without full sandboxing means untrusted pages could potentially exploit bugs in the engine.

Treat this build as an experimental toy to test web pages, follow the development, or hack on it. For more details on the project's security stance, read upstream's security policy: https://github.com/LadybirdBrowser/ladybird/blob/master/SECURITY.md


---

## Links

- [Ladybird Website](https://ladybird.org/)
- [Upstream Repository](https://github.com/LadybirdBrowser/ladybird)
- [Upstream Issue Tracker](https://github.com/LadybirdBrowser/ladybird/issues)
- [Upstream Security Policy](https://github.com/LadybirdBrowser/ladybird/blob/master/SECURITY.md)
- [Copr Repository (furqanhun/ladybird-test)](https://copr.fedorainfracloud.org/coprs/furqanhun/ladybird-test/)