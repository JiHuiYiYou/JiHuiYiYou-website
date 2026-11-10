---
title: Getting Started
description: Set up the compiler in 5 minutes and run your first program
layout: docs
project: compiler
zone: docs
---

# Getting Started

Everything below uses the **release** compiler. To build the compiler yourself, see [[Build-and-Test]].

---

## 1. Install

**The compiler runs on Windows x64.** The host must be Windows (or Wine) — this is a design
decision, not a flaw. But the **artifacts** are not limited to Windows: the SysV target produces
Linux ELF.

Go to [GitHub Releases](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/releases/latest)
and grab the latest version:

| Artifact | What it is |
|---|---|
| `jhyy-installer-*.exe` | GUI installer — the compiler, `.jhyy` file association, VS Code extension, PATH |
| `jhyy-compiler-*.msi` | The same payload, without the GUI — for enterprise / SCCM distribution |
| `jhyy-lang-*.vsix` | The VS Code extension on its own |

> **Using the compiler does not require MSYS2.** The toolchain now ships with it, so the installer
> bundles a minimal native ucrt64 toolchain. MSYS2 is only needed if you want to **build the
> compiler from source**.

Every artifact has a `SHA256.txt` checksum next to it.

---

## 2. Confirm the install

```bash
jhyy --help
```

**The first line of the output is the version banner** — this is how you confirm which compiler you
are holding.

> [!NOTE]
> **There is no `jhyy --version` option.** It never existed. Writing it prints
> `jhyy: unknown option --version` (plus a `try jhyy --help` hint), then exits with code 1.

---

## 3. Your first program

```jhyy
// hello.jhyy
extern fn puts(s: *u8) -> i32;

fn main_jhyy() -> i32 {
    puts("Hello, world!");
    0
}
```

```bash
jhyy run hello.jhyy
# => Hello, world!
```

> [!IMPORTANT]
> **The entry point is `main_jhyy`, not `main`.** A hosted program must define `main_jhyy`; its real
> signature is `main_jhyy(argc: i32, argv: *u8) -> i32`, and `argc` / `argv` may be omitted.
> The C runtime's `main` does the bridging.

---

## 4. Command line

Below is the **verbatim output** of `jhyy --help` (the help the compiler prints is in English — this
is the only version of it):

```text
jhyy compiler v{{site_version}} (self-hosted)

usage: jhyy [--target=<triple>] [--no-link] <command> [args]

commands:
  compile <file.jhyy> [-o output]   compile + link -> .exe (a lib without main is compiled only)
  build   <file.jhyy> [-o base]     compile only -> .s (no link; -o is a base name, .s appended)
  run     <file.jhyy>              compile + link + execute
  dump    <file.jhyy>              print the parsed AST tree (parse only; no sema/codegen)

flags:
  --target=<triple>  select target (default amd64_win); see targets below
  --no-link          compile to .s only, skip the link step (required for cross targets)
  --help             show this message and exit
```

In plain terms: `compile` compiles and links to a `.exe` (a library file without `main` is only
compiled, not linked), `build` only compiles to `.s` (`-o` is a base name, the `.s` suffix is
appended automatically), `run` compiles, links and executes, and `dump` only parses and prints the
AST tree (no semantic analysis, no code generation).

> [!NOTE]
> **These are two different "build"s.** `jhyy build` means "compile one `.jhyy` into assembly";
> `make all` means "build the compiler". The two are unrelated — renaming either one is a
> breaking change.

`jhyy dump` prints the **parsed AST** — one node per line, children indented, every line tagged
with `@file:line:col`. It stops right after parsing, so what you see is the **syntax**, not the
compiled form.

### Target triples

| Triple | What it produces |
|---|---|
| `amd64_win` | Hosted Windows PE/COFF — the default, and the only target this build links |
| `amd64_win_freestanding` | UEFI, no operating system |
| `amd64_sysv` | Linux SysV ABI |
| `amd64_sysv_freestanding` | Linux, no libc |

The last three produce only `.s` — link them with a toolchain that matches the target. The exact
steps are in [[Build-and-Test]].

---

## 5. The traps newcomers hit first

Every item below has a full explanation in [[FAQ]].

- **The exit code looks wrong.** MSYS2 bash truncates the exit code to 8 bits (`value & 0xFF`).
  Use the harness or Python `subprocess` to get the exit code; don't read `$?`.
- **Only one input file is accepted.** `jhyy compile main.jhyy lib.jhyy` compiles **only**
  `main.jhyy`, and the second argument is silently ignored. For several files use `import lib;`.
- **Cross targets refuse to link.** Add `--no-link` and link the `.s` yourself.
- **There is no `std::` prefix.** `import std::vec;` is a compile error — the correct form is
  `import vec;`.
- **A string literal is already a `*u8`.** No conversion is needed; `let s: [*]u8 = "x";` is a
  type error.

---

## 6. What's next

- [[Language-Tour]] — the whole language in one pass.
- [[Build-and-Test]] — build the compiler, run the tests, the gates.
- [[Architecture]] — how the compiler is put together internally.
- [[FAQ]] — frequently asked questions.
- [Language spec](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md)
  — the authoritative definition (locked; the known limitations are in its appendix B).
