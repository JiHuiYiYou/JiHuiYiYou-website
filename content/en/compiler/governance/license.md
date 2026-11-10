---
title: License
description: The exact terms of the MIT license, and the licensing status of each repository
layout: docs
project: compiler
zone: governance
---

# License

Three of the four repositories use MIT; one still has no license file. This page covers two things: what
the exact terms of MIT are, and what state each repository is actually in.

---

## The terms of MIT

All of them use the official MIT template, and the copyright line is `Copyright (c) 2026 JHYY` — the
attribution holder is the project name, not an individual.

### What is allowed

Whoever obtains a copy of the software and the documentation may **freely** use, copy, modify, merge,
publish, distribute, sublicense, and sell those copies, **without any restriction**
("without restriction"). Those eight verbs are the scope of the grant; there are no additional conditions.

### What is required

**The one and only requirement**: the above copyright notice and this permission notice must be included
in all copies or substantial portions of the Software
("The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software").

In other words: you may change the code, you may change file names, you may distribute closed source, you
may use it commercially — as long as that copyright notice and permission notice **travel with it**.

### What is not guaranteed

The software is provided "as is", **without warranty of any kind**, express or implied, including but not
limited to the warranties of merchantability, fitness for a particular purpose and non-infringement; the
author or copyright holder shall not be liable for any direct, indirect, incidental, special,
consequential, or punitive damages.

### What MIT does not cover

- No requirement to declare which modifications you made
- No express patent grant
- No interoperability exception (unlike GPL, which spells out which licenses it is compatible with)
- **No trademark rights are granted** (see the last section)

---

## Licensing status of the four repositories

| Repository | License file | Copyright line | Status |
|---|---|---|---|
| Compiler (`JiHuiYiYou-compiler`) | `LICENSE` at the root | Copyright (c) 2026 JHYY | MIT, identical to the official template |
| IDE (`JiHuiYiYou-IDE`) | `LICENSE` at the root | Copyright (c) 2026 JHYY | MIT, **byte-identical** to the Compiler one |
| OS (`JiHuiYiYou-OS`) | `LICENSE` at the root | Copyright (c) 2026 JHYY | MIT, byte-identical to the Compiler one; the only difference is that the file has no trailing newline |
| for-VEX (`JiHuiYiYou-for-VEX`) | `LICENSE` at the root | Copyright (c) 2026 JHYY | MIT, **byte-identical** to the Compiler one (added on 2026-11-08) |

The compiler repository also carries a `vscode-ext/LICENSE`, the same MIT, shipped together with the
extension.

All four repositories now carry an MIT license file (for-VEX's was added on 2026-11-08 and is
byte-identical to the Compiler one); the OS one differs only by a trailing newline.

---

## Dependencies and third-party code

MIT covers only the code JHYY wrote itself. The parts the repository owns are clean:

| Component | What it is | License |
|---|---|---|
| `compiler/src0/*.jhyy` | The compiler's only implementation | MIT (explicit) |
| `compiler/runtime/runtime.c` / `runtime.h` | The C support runtime — the one user programs link against (the hosted-mode `main → main_jhyy` bridge) | MIT (explicit) |
| `compiler/src0/jhyy_helpers.c` | The C bridge between the compiler and libc | MIT (explicit) |
| `compiler/runtime/no_std_core/*.jhyy` | The substitute implementation for `#[no_std]` (memcpy / memset / panic_handler / `__start_kernel`) — **written in JHYY, not copied over from a C library** | MIT (explicit) |

None of these four pieces of code carries third-party copyright headers, and none of them is an
implementation carried over from elsewhere.

### What really needs to be inventoried is what ships with the package

The installer ships two pieces of external code, and the two are handled differently:

| Component | Purpose | Distributed with the artifacts | Licensing status |
|---|---|---|---|
| MSYS2 ucrt64 toolchain (gcc / binutils / CRT / headers) | Assembling and linking; so that installed users do not need MSYS2 | Yes | **Documented**: the toolchain directory has a `SOURCES.txt` listing, one by one, the MSYS2 packages, their SPDX license identifiers and the source tarball URLs, plus `LICENSES/<包名>/` holding the license texts; the end of the file states "how to obtain the corresponding source" |
| .NET 8 Desktop Runtime | Needed by `jhyy-setuc` in the installer (writes UserChoice) | Yes — the installer bundles the official `dotnet-runtime-8.0.30-win-x64.exe` from the dotnetcli image, with both the version and the sha256 pinned in `installer/build.ps1` | The .NET runtime itself is MIT; the components it bundles in turn (ICU and the like) follow Microsoft's own distribution terms. **The installer's manifest does not list this one separately** ⇒ it needs to be added |

Build-time dependencies (MSYS2 / GCC / binutils / WiX / Node.js / Electron) do not ship with the
artifacts; they are only used on the development machine. But **as soon as one of them is copied into the
installer package, it enters the redistribution scope** and has to be on the manifest.

### What needs to be inventoried item by item

- The Node.js / Electron dependency trees of the IDE and the VS Code extension — `node_modules` holds
  hundreds of packages, each with its own license, and **there is currently no written manifest**
- for-VEX route B has to link the official VEX SDK (`libv5rt.a` / `stdlib_0.lib` / `lscript.ld`), which is
  VEX Robotics' own property, and **its redistribution terms are unknown**
- The kernel images the OS repository produces in the future, if they embed third-party code, need the
  same manifest

⇒ The fix can copy the style of the toolchain's `SOURCES.txt` directly: one package per line, license +
source origin.

---

## Trademarks

**There is no written trademark policy in the repository.** There is no `TRADEMARK.md`, and no file states
the usage boundaries of the logo or of the name "机会翼游 / JHYY".

Where the logo and the calligraphic lettering actually live: `vscode-ext/icon.png` / `icon.svg` /
`icon-animated.svg` / `jhyy-calligraphy.png`, `installer/assets/icons/`, and the IDE repository's
`assets/`.

MIT itself **grants no trademark rights** — what it grants is copyright and permission to use; trade
names are not covered. So until there is a written policy, work by the following boundaries (the common
practice under MIT):

| Allowed | Not allowed |
|---|---|
| Use the logo and the "机会翼游 / JHYY" wording in descriptive uses (saying "this is a tool written for JHYY" / "this is JHYY's compiler") | Suggesting official endorsement, authorization, or certification |
| Use them as-is in released artifacts | Modifying the logo (changing the proportions, the colors, adding effects) |
| Using wording such as "based on JHYY" / "for JHYY" | Registering "JHYY" as a trademark or a domain name |

**How it is meant to be filled in**: write a `TRADEMARK.md`, freeze the table above into formal terms, and
say who is responsible for maintaining it — a trademark policy without an owner is worse than no policy
at all.

---

## Related

- [Governance overview](/compiler/governance/index.html) — how decisions are made and the release cadence
- [Repository map](/compiler/governance/repo-map.html) — what each of the four repositories is responsible for
