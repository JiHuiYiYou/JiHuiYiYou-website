---
title: Download
description: The artifact matrix of the latest stable release, how to verify it, and the package manager entry points
layout: docs
project: compiler
zone: download
---

# Download

This page is the artifact matrix of the current stable release: three downloadable files, two distribution channels, and one signing note that every user runs into first. The version number on this page is authoritative; for historical releases see [archive](#archive).

> [!WARNING]
> The installer and the MSI **have no code signature**. On the first run, Windows SmartScreen shows "Windows protected your PC" — click "More info → Run anyway".
> Unsigned binaries are also more easily blocked by third-party antivirus. Enterprise distribution policies may reject unsigned MSIs outright.

Verify the hash right after downloading — the method is in [Verification and signing](/compiler/download/verify.html).

---

## Current stable release {#current}

**Current stable release v{{site_version}}**, released on {{site_version_date}}.

| Artifact | Size | What it is |
|---|---|---|
| `jhyy-installer-{{site_version}}.exe` | ~55 MB | GUI installer: compiler + `.jhyy` file association + VS Code extension + PATH + bundled ucrt64 toolchain |
| `jhyy-compiler-{{site_version}}.msi` | ~28 MB | MSI (enterprise distribution): the same payload, without the GUI wizard |
| `jhyy-lang-{{site_version}}.vsix` | ~11 KB | VS Code extension |

The sizes are measured values (taken from the artifacts in `installer/build-artifacts/` after packaging), not estimates.

Every release also ships a `SHA256.txt` asset whose contents are a manifest in `sha256sum` format.
**Verify before you run it** — the full commands are in [Verification and signing](/compiler/download/verify.html).

### Download

| File | GitHub Releases | Local mirror |
|---|---|---|
| Installer | [jhyy-installer-{{site_version}}.exe](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/releases/download/v{{site_version}}/jhyy-installer-{{site_version}}.exe) | [/downloads/jhyy-installer-{{site_version}}.exe](/downloads/jhyy-installer-{{site_version}}.exe) |
| MSI | [jhyy-compiler-{{site_version}}.msi](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/releases/download/v{{site_version}}/jhyy-compiler-{{site_version}}.msi) | [/downloads/jhyy-compiler-{{site_version}}.msi](/downloads/jhyy-compiler-{{site_version}}.msi) |
| VS Code extension | [jhyy-lang-{{site_version}}.vsix](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/releases/download/v{{site_version}}/jhyy-lang-{{site_version}}.vsix) | [/downloads/jhyy-lang-{{site_version}}.vsix](/downloads/jhyy-lang-{{site_version}}.vsix) |
| Checksum manifest | [SHA256.txt](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/releases/download/v{{site_version}}/SHA256.txt) | [SHA256SUMS.txt](/downloads/SHA256SUMS.txt) |

> [!NOTE]
> The compiler binary itself, `jhyy.exe`, is **not** a release asset — the installer puts it into `C:\Program Files\JHYY\bin\`, and in the repository it is `compiler/build/bin/jhyy.exe`.

---

## Installer (GUI) {#installer}

`jhyy-installer-{{site_version}}.exe` (~55 MB) is the one for individual users: a **WiX 4 Burn bundle**, double-clicked to walk through a graphical wizard.

It installs these things:

- **The compiler** `jhyy.exe`;
- **The `.jhyy` file association** — double-clicking a `.jhyy` file hands it straight to the compiler;
- **The VS Code extension** — installed into the user's VS Code;
- **PATH** — written into the system environment variable, so `jhyy` works in any terminal once the install is done;
- **A bundled minimal native ucrt64 toolchain** (gcc + binutils + CRT + headers), installed under `<安装目录>\toolchain\`.

The last one is the change as of v4.1.0: **MSYS2 is not needed after installing.** The toolchain manifest records gcc 15.2.0 / `x86_64-w64-mingw32`, 379 files; the compiler uses this bundled one by default and does not read the `gcc` on the user's PATH (the repository's build documentation has the search order).

The installer also ships desktop and Start menu shortcuts, documentation links, and a `jhyy-bash.cmd` — it finds bash on its own, puts `JHYY\bin` on PATH, and launches it.

Silent install (for scripts or bulk deployment):

```powershell
jhyy-installer-{{site_version}}.exe /quiet
```

`/passive` means "a progress bar but no interaction"; both are standard Burn switches.

> [!WARNING]
> The installer **has no code signature**. SmartScreen stops it on the first run — you have to click "More info → Run anyway"; the publisher field shows an unknown publisher. Third-party antivirus false positives are also more likely than for a signed binary.

---

## MSI (enterprise distribution) {#msi}

`jhyy-compiler-{{site_version}}.msi` (~28 MB) installs **exactly the same things** as the installer — the same payload packed into the same WiX MSI. There are only two differences: **no GUI wizard**, and it is **aimed at automated distribution**.

The reason it exists is software distribution policy: SCCM, Intune and group policy can push an MSI without anyone clicking "Next".

```powershell
msiexec /i jhyy-compiler-{{site_version}}.msi /qn
```

`/qn` is msiexec's silent install switch. The MSI is a **per-machine install**: it writes `C:\Program Files\JHYY` and the PATH under HKLM.

> [!IMPORTANT]
> The MSI **also has no code signature**. Some organizations' software distribution policies reject unsigned MSIs outright — this is not "it won't open", it is a policy-level block. In such an environment use [pkgmgr](#pkgmgr) or your own mirror, and talk to IT in advance.

> [!NOTE]
> The installer is bigger than the MSI because it additionally carries a copy of the .NET 8 Desktop Runtime (the Burn bootstrap and `jhyy-setuc.exe` need it). The compiler payload and the bundled toolchain are the same in both. The sizes are measured after packaging and the numbers change with the version — the table on this page is authoritative.

---

## VS Code extension {#vsix}

`jhyy-lang-{{site_version}}.vsix` (~11 KB) is the VS Code extension. Once it is installed:

- `.jhyy` files get syntax highlighting (TextMate grammar, scope `source.jhyy`);
- the editor title bar shows **Run JHYY File** (shortcut `Ctrl+F5`) and **Compile JHYY File (no run)**;
- four settings control which executable it calls, which integrated terminal it runs in, and whether it saves automatically before running.

It does **not** include a debugger, an LSP server, IntelliSense or hover documentation.

The extension is installed together with the installer or the MSI. To install it on its own:

```powershell
code --install-extension jhyy-lang-{{site_version}}.vsix
```

You can also do it inside VS Code via "Extensions → ⋯ in the top right corner → Install from VSIX".

The extension's version number is aligned with the compiler version at packaging time (`installer/vscode-ext/package.ps1` in the repository changes the `version` field of `package.json`), and the file name carries the same version number.

---

## Package managers {#pkgmgr}

Two package manager channels are available as of v4.1.4. **Both install the same Burn bundle**, and **both check the SHA-256 before running it**.

### winget

The package identifier is **`JiHuiYiYou.JHYY`**:

```powershell
winget install JiHuiYiYou.JHYY
```

> [!WARNING]
> **Upstream has not merged it yet.** The manifest was submitted to `microsoft/winget-pkgs` on 2026-11-07 (the PR is on the `jh-{{site_version}}` branch of `JiHuiYiYou/winget-pkgs`), but upstream's automatic validation and CLA signing process is not finished — as of writing this page, `manifests/j/JiHuiYiYou/JHYY` still **does not exist** in the upstream repository. So `winget install` will most likely report "no package found" for now.
> The command only takes effect after the merge.

The in-repo manifest is at `installer/distribution/winget/manifests/j/JiHuiYiYou/JHYY/<版本>/` (the three pieces: version / installer / locale).

### scoop

It uses a **personal bucket** (getting into the Main bucket is a separate decision, not made yet):

```bash
scoop bucket add jhyy https://github.com/JiHuiYiYou/scoop-bucket
scoop install jhyy --global
```

`--global` is mandatory: the installer is a per-machine install (it writes `C:\Program Files\JHYY` and the PATH under HKLM), while scoop installs into the user directory by default. Run it from an elevated shell, or accept the UAC prompt during the install.

The manifest is at `installer/distribution/scoop/jhyy.json` in the repository.

---

## Release archive {#archive}

All historical releases stay on GitHub Releases:

- [JiHuiYiYou-compiler · Releases](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/releases)

Every release carries the `SHA256.txt` of its own version. **Checksums travel with the version** — running an old version's checksum against a new version's artifact will never match.

> [!NOTE]
> The assets of the v1.5.5 / v1.5.6 releases in the archive already return 404: they are historical placeholders (those version numbers were never actually released). The other versions are available.

---

## Next {#next}

- [Targets and cross-compilation](/compiler/download/targets.html) — what each of the {{targets_count}} targets produces,
  and what freestanding actually changes.
- [Build from source and bootstrap](/compiler/download/bootstrap.html) — building the compiler from source,
  and what the self-hosted closure proves and does not prove.
- [Verification and signing](/compiler/download/verify.html) — how to check the SHA256,
  and what "no signature" means for users.
