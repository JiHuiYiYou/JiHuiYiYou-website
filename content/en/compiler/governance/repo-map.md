---
title: Repository Map
description: What each of the four repositories is responsible for, and what every directory inside the compiler repository does
layout: docs
project: compiler
zone: governance
---

# Repository Map

Four repositories, one job each. This page first draws the boundary between the four repositories, then
walks through the internal structure of the compiler repository directory by directory, and finally gives a
"if I want to change X → read Y first" lookup table.

---

## The responsibility boundary of the four repositories

| Repository | What it does | Current state | GitHub | Where the related docs are |
|---|---|---|---|---|
| **Compiler** | Language + compiler + standard library. The compiler's only implementation is in `compiler/src0/`, and the backend is a self-written amd64 emitter | Stable (self-hosted, the regression suite is green) | [JiHuiYiYou-compiler](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler) | `docs/` in the repository: the three contracts in `abis/`, `internal/FACTS.md`, `plans/v4/` |
| **IDE** | Desktop workbench. Blockly drag-and-drop blocks and CodeMirror text share one AST, and the right-hand panel hooks up the local Claude Code | Under test | [JiHuiYiYou-IDE](https://github.com/JiHuiYiYou/JiHuiYiYou-IDE) | `docs/wiki/*.zh-CN.md` in the IDE repository |
| **OS** | An operating system written in JHYY. The repository currently holds only a boot spike (`boot.s` + `BOOTX64.EFI` + `esp_root/` + `wrap_gpt.py`); the original design document was emptied out in a reorganization | Incubating | [JiHuiYiYou-OS](https://github.com/JiHuiYiYou/JiHuiYiYou-OS) | `docs/coordination/JHYY_OS侧设计终版.md` in the compiler repository |
| **for-VEX** | The VEX V5 Brain embedded target (Xilinx Zynq / Cortex-A9). The route is JHYY emitting ARM machine code directly and linking the official SDK to produce a `.bin` | Incubating (the step 0 measurement stage) | [JiHuiYiYou-for-VEX](https://github.com/JiHuiYiYou/JiHuiYiYou-for-VEX) | `docs/00-事实基线.md` and `docs/第0步-验收线.md` in the for-VEX repository |

There are only two couplings between the four: **the IDE and for-VEX depend on the compiler**; **the OS and
the compiler share an ABI** (which is why the cross-project design baseline lives in `docs/coordination/` of
the compiler repository instead of one copy per repository).

---

## The directory map of the compiler repository

### The compiler itself

| Directory | What it is responsible for |
|---|---|
| `compiler/src0/` | **The compiler's only implementation**, `.jhyy` source. The frontend (`lexer` / `parser` / `ast` / `sema` / `types` / `symtab` / `mono` / `ir` / `ffi`), the backend (`codegen` / `codegen_amd64_*`), the ABI implementation (`abi_amd64_*`) and the CLI (`main.jhyy`) are all here. **There is no C side in the repository** (the old `compiler/src/*.c` has been deleted) ⇒ there is no such thing as "parity between two implementations" |
| `compiler/src0/std/` | The user-side standard library, **{{stdlib_modules}} modules**: `mem` `fmt` `io` `math` `string` `vec` `os` `arena`. The module name is the module name, **there is no `std::` prefix** |
| `compiler/src0/jhyy_helpers.c` | The C bridge between the compiler and libc. 4 of the required FFI symbols are defined only inside `#ifdef _WIN32` with no `#else` ⇒ **the host can only be Windows** |
| `compiler/src0/bootstrap/v1.0/` | Historical material from the early self-hosting stage; not the current path |
| `compiler/src0/scripts/dev/` | Development scripts inside the source tree |
| `compiler/src0/main_run.s` | A generated assembly artifact, not hand-written |

### Runtime

| Directory | What it is responsible for |
|---|---|
| `compiler/runtime/` | **The C support runtime**: `runtime.c` (the one linked into user programs) + `runtime.h`. `no_std_core/` is the substitute implementation for `#[no_std]` (memcpy / memset / panic_handler / `__start_kernel`, all written in `.jhyy`) — in that case `runtime.c` **does not take part in linking** |
| `runtime/linux_elf/` | Another `runtime` at the repository root: **the static, libc-free Linux ELF64 runtime for the `amd64_sysv_freestanding` target** (`crt0.S` + `link.ld`). It is not the same thing as `compiler/runtime/`; the names just collide |

### Tests and artifacts

| Directory | What it is responsible for |
|---|---|
| `compiler/tests/examples/` | The sources of the regression cases (`.jhyy`); the ones whose names start with an underscore are helper fixtures, not cases |
| `compiler/tests/golden/` | AST golden files (`*.ast.txt`) |
| `compiler/tests/bootstrap/` | The self-hosting and cross-validation scripts: `closure_check.sh` (cross-generation closure), `fixed_point.sh` (cross-generation fixed point), `byte_equal.sh`, `artifact_checks.sh` (artifact-level assertions), `artifact_fresh_check.sh` (committed artifact vs freshly built artifact), `sysv_*.sh` (SysV ABI gates), `bench.sh`, `mutation_test.py` |
| `compiler/build/` | The build artifacts: `bin/` (`jhyy.exe` is the **git-tracked self-hosting anchor**), `obj/`, `regalloc/`. Change `src0` without committing a new binary and CI's `artifact-fresh` gate turns red |
| `regress.py` | The regression driver at the repository root |
| `Makefile` | At the repository root. `make` = build the C bridge + iterate the self-hosting closure to a fixed point |

### Documentation

| Directory | What it is responsible for |
|---|---|
| `docs/abis/` | **The three contracts**: language spec v{{spec_version}} (locked), ABI v{{abi_version}} (locked), binary format v{{binary_format_version}} (**design draft, not implemented**) |
| `docs/internal/` | Internal documentation: `FACTS.md` (the single source of truth for facts), `workarounds.md` (the workaround ledger, **never archived**), `architecture.md`, `build.md`, `feedback-codes.md`, `README.md` (the documentation index) |
| `docs/archive/` | The historical archive: `logs/` (the changelog + sprint logs of each axis), `plans/` (the sprint plans of each axis), `perf/` (performance measurements that have been superseded), `audit/` (a deep review of codegen + RCAs). **The archive is not edited** — it describes the world as it was then |
| `docs/plans/v4/` | The current plan line; one `vX.Y.Z-plan.md` per version slot |
| `docs/coordination/` | The cross-project design baseline (one final version each on the compiler side / the OS side) |
| `docs/perf/` | The current performance baseline (frame size / memory-access share / regression ratio) |

### Tools and distribution

| Directory | What it is responsible for |
|---|---|
| `vscode-ext/` | The VS Code extension `jhyy-lang`: TextMate syntax highlighting + native run / compile commands + terminal profile detection. `jhyy-lang-*.vsix` are the built artifacts |
| `mcp-jhyy/` | The MCP service for Claude Code (compile / run / inspect the IL / query the ledger / run the regression), implemented in Python, gated by `mcp-pytest` |
| `installer/` | Windows installation: WiX (Burn bundle EXE + MSI) + the bundled ucrt64 toolchain + `release-notes/` (the body of each release note) + `distribution/` (scoop / winget manifests) + `GUIDS.md` (the installer's GUID registry) |
| `scripts/dev/` | The gate scripts and development tools: `bump_version.py` (version automation), `check_arch_claims.py`, `check_spec_consistency.py`, `check_binary_format_layout.py`, `check_regalloc_parity.py`, `docs_facts_check.py`, `audit_test_assertions.py`, `check_regress_facts.py`, `test_docs_gate_mutations.py`, `bench/runtime_perf.py`, `regalloc_reference.py` |
| `bench/` | The benchmark suite: `tasks/` (the problems), `bench.py` (the driver), `difftest.py` (random-program differential testing), `METHODOLOGY.md` (the measurement conventions), `seeds/`, `baseline/` |

There are a few more files at the repository root, each responsible for one thing: `VERSION` (the single
source of truth for the version number), `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`,
`CODE_OF_CONDUCT.md`.

---

## If I want to change X, read Y first

| If I want to change… | Read first | Then read |
|---|---|---|
| Language syntax or semantics | `docs/abis/jhyy-lang-spec-v4.0.0.md` (the body + appendix B) | `compiler/src0/parser.jhyy` / `sema.jhyy`; contract changes go through a proposal |
| FFI, struct passing, calling convention | `docs/abis/jhyy-abi-v4.0.0.md` | `compiler/src0/abi_amd64_*.jhyy` |
| The backend (codegen / emission) | `docs/internal/architecture.md` | `compiler/src0/codegen_amd64_*.jhyy`; touching `src0` ⇒ the release-level process |
| Diagnostic messages, error wording | `docs/internal/workarounds.md` (check whether it is a known problem first) | `compiler/src0/lexer.jhyy` / `sema.jhyy` |
| The standard library | `compiler/src0/std/*.jhyy` (the real API is here, not in the docs) | `docs/internal/workarounds.md`; changing a stable API goes through a proposal |
| The build, the toolchain, the gates | `docs/internal/build.md` | `Makefile`, `scripts/dev/`, `.github/workflows/` |
| The `.jhyynb` binary format | `docs/abis/jhyy-binary-format-v1.0.0.md` (**design draft, not implemented**) | `scripts/dev/check_binary_format_layout.py` |
| The installer and distribution | `installer/README.md` | `installer/build.ps1`, `installer/wix/`, `installer/distribution/` |
| The VS Code extension | `vscode-ext/README.md` | `vscode-ext/src/`, `syntaxes/` |
| The MCP service | `mcp-jhyy/README.md` | `mcp-jhyy/server.py` |
| Benchmarks and measurement conventions | `bench/METHODOLOGY.md` | `bench/tasks/`, `bench/bench.py` |
| OS-related design | `docs/coordination/JHYY_OS侧设计终版.md` | `docs/coordination/JHYY_编译器侧设计终版.md` |
| Citing "a number that changes" | `docs/internal/FACTS.md` | — (do not restate it elsewhere; restating it is how it drifts) |
| Knowing "why this line was written that way" | `docs/archive/` (look up the changelog and the RCAs by axis) | — |

---

## Related

- [Compiler implementation](/compiler/docs/compiler.html) — how the pipeline and the backend run
- [Build and test](/compiler/docs/build-and-test.html) — how to get it running
- [Contributing guide](/compiler/community/contributing.html) — the concrete steps for filing an issue and opening a PR
- [License](/compiler/governance/license.html) — the licensing status of each repository
