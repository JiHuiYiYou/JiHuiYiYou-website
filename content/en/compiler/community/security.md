---
title: Security disclosure
description: How to report a security issue, and the known trust boundaries
layout: docs
project: compiler
zone: community
---

# Security disclosure

This page covers two things: **how to report a security issue** (without turning it into a public exploit), and **the trust boundaries this project knows about** (where the compiler gives you no guarantees).

The original is the repository's [`SECURITY.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/SECURITY.md), and this page is a reading guide for it.

---

## The one-line version

> **Do not open a public issue for a suspected vulnerability.** Use the
> [private advisory form](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/security/advisories/new).

Public issues get indexed, mirrored and cached — **within minutes**. A public report can turn a fix into an exploit before the patch even exists.

---

## Reporting channels

| Priority | Channel |
|---|---|
| Preferred | [GitHub private advisory](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/security/advisories/new) — only you and the maintainer can see it |
| Fallback | Email **15901598712@163.com**, with the same information, and **ask for an acknowledgement** |

### What to include in the report

| Item | Why it matters |
|---|---|
| **Version** — the `VERSION` file at the repository root, or the first line of `jhyy --help` | The fix lands on the latest release first |
| **Reproduction** — the complete `.jhyy` source, or the exact command line | A one-line diff is the difference between "fixed the same day" and "a week of back-and-forth" |
| **Actual vs expected** | What happened, and what should have happened |
| **Exit code** | See the trap below |
| **Origin** — a released binary, or a self-hosted build | The two may behave differently |
| **Impact** — what the attacker gets, and what they need first | It decides severity, and severity decides the deadline |

> [!WARNING]
> **Take the exit code from the harness or Python `subprocess`, do not read MSYS2 bash's `$?`.** bash truncates the exit code to 8 bits (`value & 0xFF`), so expected codes ≥ 256 have to be reduced first: 827 → 59, 501 → 245, 300 → 44, 1000 → 232. A lot of "the exit code is wrong" reports are just this.

**You do not need to prove exploitability.** A source-level demonstration is enough — "here is the `.jhyy` file that makes the compiler write out of bounds" is a complete report.

---

## What counts as a vulnerability

**Counts:**

- **Memory-safety violations in the generated code** — for programs that **do not do these things themselves**: the compiler emits an out-of-bounds write, reads or writes uninitialized memory, corrupts the stack, or computes a wrong address.
- **Memory safety inside the compiler** — a crafted `.jhyy` source file (or any other input file the compiler reads) makes the compiler corrupt its own memory, write out of bounds, or execute attacker-controlled bytes. The compiler parses untrusted input, and that input should not be able to take over the process.
- **Code execution through the toolchain** — making the compiler run code the user did not intend to run: an import that resolves to an unexpected file, an argument passed unsanitised to an external program, a build directory whose contents can steer the build elsewhere.
- **Path traversal in the installer or the released artifacts** — writing outside the directories it is supposed to touch.
- **Release integrity** — the published `SHA256.txt` does not cover the artifact shipped with it, or the released artifact does not match what the tagged source produces.

**Does not count:**

- **Misuse of unsafe features the documentation calls out** — unchecked slice indices, an `extern fn` declared with the wrong C signature, hand-written `asm!`, `#[naked]` functions. The documentation makes clear that these are sharp-edged tools.
- **Gaps at the language level** — no borrow checking yet, no float formatting, `Vec<T>` is not element-generic yet. These are recorded in **appendix B** of the language spec and in the public [workaround ledger](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/workarounds.md), and are not vulnerabilities.
- **Crashing on input you control, with no memory-safety impact** — that is a bug; report it as an issue. (Unless the crash can be triggered from **source files you did not write**.)
- **Bugs in the generated program's own logic.**
- **Vulnerabilities in the third-party toolchain bundled in the Windows installer** — report them upstream; if you think **the act of bundling itself** introduces problems of its own, tell us too.

---

## Which versions are supported

| Line | Support status |
|---|---|
| **Latest release** | Security fixes are provided |
| Earlier releases | None — please upgrade to the latest |
| `main` (unreleased) | Best effort, fixes ship with the next release |

This page **deliberately carries no version numbers**: only "the latest release" is ever the supported one. The version facts are carried by the [download page](/compiler/download/index.html).

---

## What happens after you report

| Stage | Target |
|---|---|
| Acknowledge that the report was received | **7 days** |
| Triage — is it a vulnerability, and how severe | **14 days** |
| Release the fix for critical / high severity | As soon as CI is green — **no fixed date**, but it will not be deliberately withheld |
| Release the fix for medium / low severity | The next release |

**These are targets, not guarantees** — this is a one-person project, and the other person has a day job. If the window passes with no acknowledgement, **that is itself a defect in this process**: say so in the same thread, and consider that the silence is worth escalating.

**Even if the conclusion is "not a vulnerability", you will still get the triage result** — a reasoned "no" is a real answer, and more useful than silence.

### Public disclosure

- **Give the maintainer a reasonable window before going public.** The default expectation is **90 days from the first report**. If you need more time it can be negotiated, and an explicit extension is possible.
- **If there is a mitigation before the fix** (for example "don't use a build you don't trust to compile `.jhyy` files you don't trust"), it is published **immediately** in the advisory — **you will not be asked to keep it secret**.
- **Attribution** is up to you: any name or handle is fine, and no attribution is fine too.
- **If it is already public**, say so in the report — that changes the disclosure timeline, not whether it will be fixed.

---

## Known trust boundaries

What follows are facts that can be confirmed from the state of the project. Their use is to let you know **what "vulnerable" means in this project**.

| Boundary | Fact | What it means for the user |
|---|---|---|
| **The installer and the MSI are unsigned** | There is no code signing | Windows SmartScreen blocks the first run; **supply-chain trust rests on manually checking the SHA256** — see [Verification and signing](/compiler/download/verify.html). Unsigned binaries are also more likely to be flagged by third-party antivirus |
| **No GC, no managed runtime** | Memory safety rests on **arena lifetime discipline + limited borrow checking** | **Not a Rust-level guarantee**. Borrow checking currently covers only "a repeated `&mut` on the same variable within the same scope"; full NLL / Polonius borrow checking, lifetime annotations `'a`, reborrow and cross-function borrows are all unimplemented (spec appendix B) |
| **Write protection for immutable bindings is unimplemented** | The compiler does not check whether the object whose address is taken is mutable | `&x` on an immutable binding is legal; writing through such a pointer **neither errors nor takes effect** |
| **C-side parameter types of `extern fn` are not checked** | Parameters / return types are unrestricted | Declaring `extern fn takes(s: MyStruct) -> i32;` compiles, and **the struct is actually passed by address**, which does not match the C ABI. Argument types are not checked either — `f(5)` passed to a struct parameter compiles, and at runtime the register is read with the struct layout |
| **The generated code carries no extra hardening** | The compiler inserts no stack canary and no guard page | Whatever the linker imposes is what you get |
| **The compiler has no sandbox** | It runs with your user privileges and parses untrusted input | A `.jhyy` source file of unknown origin is untrusted input, exactly as it would be for any other parser |
| **The compiler shells out to an external C toolchain** | Resolution order: the `JHY_GCC` environment variable → `env.txt` → the bundled toolchain → `C:\msys64` → `PATH` → bare `gcc` | Pointing that override at an untrusted binary means running that binary. **Environment variables are part of the trust boundary** |
| **`jhyy run` executes the program it just compiled** | Compiling and running untrusted source = running untrusted code | The compiler provides no isolation |
| **No network access, no telemetry** | It opens no socket, sends nothing, and reads no credentials | It only reads the toolchain path overrides and two debug switches |
| **The installer bundles a third-party native toolchain** | That is its own supply-chain surface | It is covered by the checksum shipped with each release, **not** by keeping a vendored copy in the repository |

> [!NOTE]
> The arena is **not** "arena only, no free": JHYY's arena provides both `arena_reset` (reuse the memory, the block is not released) and `arena_free` (release the whole block). Do not copy another language's arena model.

---

## Compiler bug or user-program bug?

| Situation | Where to report it |
|---|---|
| **The compiler did the wrong thing** — wrong output, a crash, a diagnostic that makes no sense | An ordinary issue, written in the reproduction format of the [contributing guide](/compiler/community/contributing.html) |
| **Your own `.jhyy` program computed the wrong thing** | Not a compiler bug. **The regression suite covers the compiler's own behaviour; it does not mean your program has no undefined behaviour** — check the semantics against the language spec first |
| **A gap at the language level** (no borrow checking, no float formatting, `Vec` is not generic) | Recorded in spec appendix B and in the public ledger — not a security issue |
| **A known limitation you want to work on** | The roadmap is public, see `FACTS.md` § 4; open an issue describing your approach |
| **A workaround that should go into the ledger** | The ledger is maintained in public, `docs/internal/workarounds.md`, **entries are only added, never removed** |
| **A security issue** | Use the private advisory channel above, **do not** open a public issue |
| **A vulnerability in a third-party toolchain** | Report it upstream; but if you think **the way it is bundled** is itself a problem, tell us too |

---

## What is still missing

- **No written-out archive page for security advisories, no credits page, no security mailing list.** Advisories currently exist only on GitHub, with no second archive. We are working on this.
- **No written-out process for CVE numbering.**
- **No backport commitment for security fixes to older versions** — the policy is "upgrade to the latest release".

---

## Next

- [Contributing guide](/compiler/community/contributing.html) — how to report an ordinary bug.
- [Code of conduct](/compiler/community/conduct.html) — the reporting channels and the enforcement ladder.
- Original: [`SECURITY.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/SECURITY.md)
