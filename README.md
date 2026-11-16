# Ladybird for Fedora

This repo got the recipe to build Ladybird on fedora. The spec file uses CalVer release tags from upstream repo. And also uses the upstream profile for Distributions.

> [!WARNING]
> Ladybird is a pre-alpha browser. DON'T USE IT FOR DAILY DRIVING OR BANKING OR ANYTHING IMPORTANT. It doesn't even have all the basic web security features yet.


---

## Installation

Ladybird can be installed through the github artifacts of upstream repo: https://github.com/LadybirdBrowser/ladybird/actions/workflows/build-release.yml

Or you can use my copr repo which i'd occasionally update until Ladybird goes stable and gets shipped in fedora repos:

```sh
sudo dnf copr enable furqanhun/ladybird-test
sudo dnf install ladybird
```

---

## Why Rawhide is Not Supported (Yet)

There are two main reasons:

First is rust and `-Dwarnings`. upstream ladybird passes `-Dwarnings` to `rustc` by default in their cmake files (`Meta/CMake/rust_crate.cmake`). Rawhide ships the newest compiler versions, and whenever a new rust release deprecates an api, rustc throws a warning. even though the code works completely fine, `-Dwarnings` treats any warning as a hard error and kills the build. we can patch this pretty easily by passing `-Adeprecated` so it ignores deprecation warnings, but that leads right into the second problem.

The bigger blocker is cargo. cargo 1.100 dropped an internal cache file called `root-output`. Ladybird's build system (`Meta/CMake/sync_rust_ffi_header.cmake`) expects `root-output` to be there so it can find where cargo put `RustFFI.h` and sync it. with newer cargo, that file doesn't exist anymore, so cmake crashes when it can't find the header. and because fedora's rawhide repos only keep the single newest version of packages, we can't just tell dnf or copr to grab an older cargo/rust snapshot.

That can be patched too tbh, but it's better to wait. So until upstream updates their cmake scripts to stop relying on internal cargo files, rawhide builds will be paused. Fedora 43, 44, and 45 work fine.


---

## Pre-Alpha Warning & Security

Once again, Ladybird is a pre-alpha browser that is still very early in development.

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