---
title: Docs home
description: JHYY docs home — start here
layout: docs
project: compiler
zone: docs
---

# JHYY (机会翼游) — Wiki

**A self-hosted, statically typed, expression-oriented systems programming language.**

This wiki is the long-form version of the repository README: guides, a tour, and the
answers to the questions that keep coming back. The README is the map; this is the
walkthrough.

> **Nothing here is the source of truth — the repository is.**
> Numbers, schedules, and known limitations change; this wiki is only **a guide to
> where the truth lives**.
> Every page points at the document that actually owns that fact.
> If a wiki page conflicts with a repository document, **the document wins** — please
> open an issue and we will fix the page.

---

## Start here

| You want to… | Go to |
|---|---|
| Install the compiler and run your first program | [[Getting-Started]] |
| Learn the language | [[Language-Tour]] |
| Build the compiler from source and run the tests | [[Build-and-Test]] |
| Understand how the compiler is put together | [[Architecture]] |
| Find the answer to a recurring question | [[FAQ]] |
| Contribute a fix or a feature | [CONTRIBUTING.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/CONTRIBUTING.md) |
| Report a security issue | [SECURITY.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/SECURITY.md) |

---

## The project in one paragraph

JHYY is a systems programming language **written in itself**. `compiler/src0/*.jhyy`
is the compiler's only implementation — there is no bootstrap C compiler in the tree,
and no vendored backend. The compiler compiles itself first, then lets the compiler it
produced compile itself again, and the gate requires that the assembly the two
generations produce is **byte-identical**. The fixed point is **run**, not assumed.

The backend is a **self-written amd64 code generator**. It emits PE/COFF on Windows and
ELF on Linux. There is no LLVM, no QBE, no garbage collection, and no managed runtime;
the bundled runtime is only a very small C support library.

For the full version, read the
[README](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/README.md)
(the Chinese version is
[README.zh-CN.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/README.zh-CN.md)).

---

## Three things that are different

1. **The self-hosting is verified.** Not "the compiler can compile itself", but "the
   second generation is byte-identical to the first" — checked on every build, and the
   result is published along with every release.
2. **No vendored backend.** The amd64 code generator is JHYY's own code. The
   intermediate representation it consumes is also JHYY's own format: it borrowed QBE's
   **syntax** as a starting point, but no QBE code is vendored, linked, or executed.
3. **No GC, no managed runtime.** Explicit pointers, a predictable C-like ABI, and a
   `no_std` mode for freestanding targets.

---

## Where the truth lives

| Question | Document |
|---|---|
| Current version, regression baseline, schedule | [`docs/internal/FACTS.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md) — the single source of truth for every number that changes |
| How to write `.jhyy` | [Language spec](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md) (locked) |
| FFI, struct layout, calling convention | [ABI whitepaper](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-abi-v4.0.0.md) (locked) |
| Known compiler defects and workarounds | [workaround ledger](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/workarounds.md) |
| How the compiler is put together | [Architecture overview](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/architecture.md) |
| How to build, test, and release | [Build and run](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/build.md) |
| What changed in each version | [CHANGELOG.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/CHANGELOG.md) |
| The current plan, laid out by version | [`docs/plans/v4/`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/tree/main/docs/plans/v4) |

---

## How this wiki is maintained

The wiki is a **hand-written companion document**, not a generated artifact — its order
of explanation differs from the repository's, and it is allowed to be more
conversational. Three rules keep it honest:

1. **It does not repeat numbers.** A wiki page that copies down a version, a count, or
   a size is wrong the day after it is written. The page instead points at the
   document that owns that number.
2. **It does not repeat the ledger.** Known limitations live in Appendix B of the
   language spec and in the public workaround ledger; the wiki only points the way.
3. **Corrections are welcome.** If a page conflicts with the repository, the repository
   is right — open an issue and say which page is out of date.
