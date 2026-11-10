---
title: Build and test
description: Build the compiler from source, run the regression suite and the self-hosted closed-loop gate
layout: docs
project: compiler
zone: docs
---

# Build and Test

This page is about **changing the compiler**. To merely **use** the compiler, see
[[Getting-Started]].

---

## Requirements

**Host:** Windows 10 + MSYS2 (`C:\msys64\mingw64\bin\bash.exe`), plus
`mingw-w64-ucrt-x86_64-gcc` and `mingw-w64-ucrt-x86_64-binutils`.

```bash
pacman -S --needed mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-binutils
```

> [!IMPORTANT]
> **Do not** use the MinGW `gcc` that ships with Git Bash
> (`/c/Program\ Files/Git/mingw64/bin/gcc.exe`) — it does not support PE+ linking and
> fails at the link stage.

---

## Building

```bash
git clone https://github.com/JiHuiYiYou/JiHuiYiYou-compiler.git
cd JiHuiYiYou-compiler
make all        # → compiler/build/bin/jhyy.exe
```

`make` does more than compile: it **iterates the self-hosted closed loop to a fixed
point**. The compiler compiles itself, the compiler it produced compiles itself again,
and the build keeps iterating until two consecutive generations produce
**byte-identical** assembly. This is the foundation the whole project stands on — the
fixed point is run, not assumed.

`make clean` removes the build artifacts.

The full toolchain story — lookup order, the classic pitfalls, multi-target builds,
version-number automation — is in the repository's
[build documentation](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/build.md).

---

## Testing

```bash
python regress.py                       # full suite
python regress.py --tests=hello.jhyy    # a single case
python regress.py --all                 # includes the gated cases
python regress.py --byte-equal          # compares the .il / .s / .exe layers
python regress.py --fixed-point         # cross-generation fixed point check
```

> [!IMPORTANT]
> **Run the tests from the repository root.** The script resolves paths against the
> current directory; running it in a subdirectory reports every file as missing, which
> looks like drift but is not.

The tests cover every `.jhyy` file under `compiler/tests/examples/` (except helper
fixtures whose names start with an underscore). The pass counts and the list of gates
are written in
[FACTS.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md)
— the only place where numbers are written down.

### Assertion strength

```bash
python scripts/dev/audit_test_assertions.py --strict
```

A test that cannot fail is worse than no test — it checks nothing yet reports success.
This audit reports how many cases carry real assertions, and goes red when a
zero-signal case shows up.

---

## The gates

The project knows that "all tests green" is weaker than it sounds, so there is a ring
of **gates** around it. The complete and current list is in
[FACTS.md § 2](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md)
— the CI gates and the local gates that have to be run by hand are listed there
separately.

The three worth knowing:

| Gate | What it proves |
|---|---|
| **Self-hosted closed loop** | The compiler reproduces itself exactly — a statement about generation determinism, not about semantic correctness |
| **Artifact freshness** | The `jhyy.exe` committed to the repository behaves the same as one freshly built from the current source |
| **Full regression** | Actual semantics — a semantic regression is what this gate catches |

> [!NOTE]
> "The compiler compiles itself byte-identically" **does not** mean the compiler is
> right. A deterministic wrong compiler can close the loop perfectly. This is the
> classic "trusting trust" gap, covered by a different gate: the regression suite.

---

## Cross-compiling to Linux

The output is not limited to Windows. The `amd64_sysv*` targets produce SysV assembly
that can be linked and run on Linux, in three steps:

```bash
# 1. on Windows — emit the .s (a cross target must not be linked)
./compiler/build/bin/jhyy.exe compile --target=amd64_sysv_freestanding --no-link prog.jhyy -o prog
#    ⇒ prog.s

# 2. on Linux — link it into a static ELF
gcc -nostdlib -static -T runtime/linux_elf/link.ld -o prog.elf \
    runtime/linux_elf/crt0.S prog.s

# 3. run it
./prog.elf
```

This is exactly the chain CI runs on Linux — see
[`compiler/tests/bootstrap/sysv_link_run.sh`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/compiler/tests/bootstrap/sysv_link_run.sh).

The Linux runtime calls `main_jhyy` (not `main`) and exits with its return value, so
the entry convention matches the hosted side — but the link uses `-nostdlib`, so a
freestanding program cannot call libc.

---

## Releasing a version

The version number is **not hand-edited**. The `VERSION` file at the repository root is
the single source of truth, and this order cannot be reversed:

```bash
python scripts/dev/bump_version.py set <new version>   # ① bump VERSION and the version strings everywhere
make                                            # ② the compiler compiles the version in
pwsh -File installer/build.ps1 bundle           # ③ build the artifacts
python scripts/dev/bump_version.py finalize     # ④ fill in the measured checksums and sizes
python scripts/dev/bump_version.py check        # ⑤ zero-drift gate
```

> [!WARNING]
> **Step ② cannot be skipped.** The version is a string literal in the compiler source,
> so the self-hosted artifact has to be rebuilt — otherwise the compiler still reports
> the previous version, and the drift gate in step ⑤ will (correctly) go red.

---

## Companion tools

### The MCP service for Claude Code

`mcp-jhyy/` exposes the compiler to AI coding assistants: compile, run, check syntax,
dump the intermediate representation, run the regression suite, query the workaround
ledger, and look up the language spec and the ABI.

```bash
pip install fastmcp     # ⚠️ not `mcp[cli]` — fastmcp is a different distribution package
```

Details are in
[mcp-jhyy/README.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/mcp-jhyy/README.md).

### The VS Code extension

`vscode-ext/` provides syntax highlighting, a native ▶ **Run JHYY File** command
(`Ctrl+F5`), and a **Compile JHYY File (no run)** command. The extension is installed
along with the compiler installer package.

---

## Next

- [[Architecture]] — what `make` actually builds.
- [[FAQ]] — questions about building and running.
- [CONTRIBUTING.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/CONTRIBUTING.md)
  — the contributor workflow.
