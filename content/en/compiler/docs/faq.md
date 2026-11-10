---
title: FAQ
description: Questions that keep coming back, and their answers
layout: docs
project: compiler
zone: docs
---

# FAQ

The questions that keep coming back, and the answers that are true right now. When an
answer changes, the repository has the final say — see the authoritative versions in
the
[language spec](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md)
and [FACTS.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md).

---

## Using the compiler

### Can the compiler run on Linux or macOS?

Not directly. **The compiler is a Windows program** — `jhyy.exe` is a PE executable, so
the host must be Windows (or Wine). This is a deliberate design decision, not an
oversight.

**What is portable is the output**: the SysV targets produce Linux ELF assembly, and CI
links and runs it on Linux. So "a JHYY program can run on Linux" holds; "the JHYY
compiler can run on Linux" does not hold today.

### How do I check the version?

**The first line of `jhyy --help`** is the version banner. There is no `jhyy --version`
option — it never existed; typing it prints `jhyy: unknown option --version` and then
exits with 1.

### Why is the entry point `main_jhyy` and not `main`?

Because the hosted entry point has a different signature:
`main_jhyy(argc: i32, argv: *u8) -> i32`, where `argc` / `argv` may be omitted. The C
runtime's `main` does the bridging. The freestanding Linux runtime follows the same
convention — `crt0.S` calls `main_jhyy` and exits with its return value.

### Why does `jhyy compile a.jhyy b.jhyy` ignore `b.jhyy`?

Because the compiler **only accepts one input file**; extra `.jhyy` arguments are
silently ignored — no error, no warning. To compile multiple files, use `import`: write
`import lib;` in `main.jhyy`, and the compiler pulls `lib.jhyy` in along the import
graph.

### Why does my exit code look wrong?

If you read `$?` under MSYS2 bash, it has been truncated to 8 bits (`value & 0xFF`).
Use a harness or Python `subprocess` to get the exit code instead. An expected 827
comes back as 59, 501 as 245, 300 as 44, 1000 as 232.

### Why doesn't the compiler link my Linux program for me?

**This build cannot link cross targets** — the bundled linker always produces a Windows
`.exe`. Add `--no-link` and link the `.s` yourself with a matching toolchain; the
three-step procedure is in [[Build-and-Test]].

### Do I need MSYS2 to use JHYY?

No. The installer ships a minimal native toolchain, so an end user only needs Windows.
MSYS2 is needed only to **build the compiler from source**.

---

## Language

### Is there garbage collection? Allocators? RAII?

**No GC, no automatic ownership, no RAII.** Memory is explicit: raw pointers, manual
allocation, and — if you want it — the arena allocator in the standard library, plus
`defer` for scope-exit cleanup. `defer` runs LIFO on scope exit, but **it does not run
on an implicit tail return**.

### Why is there no `std::` prefix?

Because `import` takes the module name directly: `import vec;`, not `import std::vec;`.
Writing the prefixed form is a compile error.

### Can I call C libraries?

Yes — `extern fn` calls C functions with the C ABI. Two caveats: **there is no variadic
form** (every argument has to be written out one by one), and **argument types are not
checked against the C signature**, so a mistake still compiles and only shows up at
runtime.

### Can I write closures that capture variables?

Not yet — capturing is a **compile error** today. Block-expression closures exist; they
just cannot capture.

### Are generics and traits done?

Generics are partly there; **traits are not implemented yet**. Both are on the public
roadmap — the current schedule is in
[FACTS.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md).

### What about floating point?

`f32` and `f64` exist as types, but the standard library **has no floating-point
formatter yet** — so today you cannot print a float.

### Is JHYY production-ready?

**Not yet.** The project is pre-1.0: the self-hosted closed loop runs, the regression
suite is green, but the language spec is still moving and no semantic stability across
versions is promised. The README has a status table of what works and what does not.

---

## Project

### If the intermediate representation is "QBE-style", why is there no QBE?

Because what was borrowed is QBE's **syntax**, which is concise and readable. QBE
itself has been removed from the project: the amd64 backend is JHYY's own code, and
the IL text is JHYY's own format. No QBE code is vendored, linked, or executed.

### Does "the compiler compiles itself byte-identically" mean the compiler is correct?

**No.** It says the compiler **reproduces itself exactly** — that is a statement about
generation determinism. A deterministic wrong compiler can close the loop perfectly.
This is the classic "trusting trust" gap, covered by a different gate: the regression
suite.

### Why does the repository publicly maintain a ledger of known defects?

Because a compiler that quietly works around its own defects is worse than one that
publicly admits them. The ledger
([workarounds.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/workarounds.md))
is maintained in public: every entry spells out what the problem is, when it triggers,
how to work around it, and what can replace that workaround. Entries are only closed,
never deleted — it is an audit trail.

### How do I report a bug?

Include a **minimal reproduction**, the expected output and the actual output, the
version, and the exit code. Details are in the
[contributing guide](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/CONTRIBUTING.md);
the issue template asks for exactly these fields.

### How do I report a security issue?

**Do not open a public issue.** Use the private advisory form instead — the process,
the scope, and the response-time table are all in
[SECURITY.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/SECURITY.md).

### Where is the roadmap?

The authoritative schedule is in
[FACTS.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md),
and one plan per version slot is in
[`docs/plans/v4/`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/tree/main/docs/plans/v4).
The numbers on reserved versions are placeholders — every plan carries its own
"checklist at kickoff"; when you pick up that slot, re-verify against the situation at
that time.

---

## Still stuck?

- [Discussions](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/discussions) — questions and design discussion.
- [Issues](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/issues) — bugs and feature requests.
- [[Home]] — back to the start.
