---
title: Reference Overview
description: The entry points to the three kinds of reference — language, contracts, toolchain — and what each one guarantees
layout: docs
project: compiler
zone: docs
---

# Reference Overview

This page is the index of the "language reference" group. JHYY's reference material comes in three
layers, and each layer guarantees something different — read them mixed together and it is easy to
confuse "how do you write this language" with "how do two artifacts recognize each other".

## The three layers of reference

| Layer | What question it answers | What it guarantees | Version nature |
|---|---|---|---|
| **Language spec** | Syntax and semantics | What a legal program is, what each expression means, which behaviours are defined | **A locked contract** |
| **ABI** | Type layout, calling convention, linking rules | How the compiler, artifacts and external libraries recognize each other | **A locked contract** |
| **CLI / standard library** | How to use the concrete tools and APIs | How the commands are typed, what the functions are called, what they return | Follows the toolchain version |

The first two layers are **contracts**: an implementation must obey them, and only then is it
"JHYY". The third layer is **usage** — it evolves with the toolchain and carries no stability
promise.

---

## Contract version ≠ toolchain version

This is the thing people get most easily tangled up in.

**Language spec v{{spec_version}}** and **ABI v{{abi_version}}** were each locked on 2026-10-24, together with
`v4.0.0 final`. The toolchain is a separate line — the current stable version is
v{{site_version}} (the version changes; the [download page](/compiler/download/index.html) is
authoritative).

In other words:

> **v4.1.x is an evolution of the implementation of the v{{spec_version}} contract, not a modification of the
> contract.**

A newer compiler may support one more syntactic sugar or fix one more bug, but as long as the spec
and the ABI are still v{{spec_version}}, the rules by which artifacts recognize each other have not changed by
a single word. Conversely, the day the spec goes to v5.0.0 that is a **new contract**, and the
compatibility of old artifacts has to be assessed separately.

One corollary: **which document you should cite while writing code depends on who you need to be
recognized by.**
Recognized by another JHYY artifact → look at ABI v{{abi_version}}. Recognized by a C library → also look at
ABI v{{abi_version}}. Just want to know "how to write it" → look at spec v{{spec_version}}.

---

## The four references

| Reference | What it covers | Authoritative original |
|---|---|---|
| [Language spec v{{spec_version}}](/compiler/docs/spec.html) | Syntax, type system, semantic boundaries | [`docs/abis/jhyy-lang-spec-v4.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md) |
| [ABI v{{abi_version}}](/compiler/docs/abi.html) | Type layout, calling convention, linking rules | [`docs/abis/jhyy-abi-v4.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-abi-v4.0.0.md) |
| [Standard library](/compiler/docs/stdlib.html) | The real API of the {{stdlib_modules}} modules | [`compiler/src0/std/`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/tree/main/compiler/src0/std) |
| [CLI reference](/compiler/docs/cli.html) | Commands, arguments, exit codes | The CLI section of the repository's `README.md` |

If you have not read the spec yet, starting from the [language tour](/compiler/docs/tour.html) is
faster; to get your first program running, see [getting started](/compiler/docs/getting-started.html).

---

## The docs are not the source of truth — the repository is

This page, this group of references, and the whole site wiki are **hand-written companion
documentation**. Their job is to tell you "which file the fact lives in", not to restate the fact.

The reason is simple: numbers that change (version numbers, regression baselines, the list of
limitations) copied into a second document mean that the next day there are two numbers that
contradict each other, and the reader has no way to know which one to believe.

So every assertion has to be traceable to a file:

| Kind of fact | Where it lives |
|---|---|
| Numbers and schedules that change | [`docs/internal/FACTS.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md) |
| Known limitations and workarounds | [`docs/internal/workarounds.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/workarounds.md) |
| What each version changed | [`CHANGELOG.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/CHANGELOG.md) |
| How the compiler is put together | [`docs/internal/architecture.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/architecture.md) |

Repository: [github.com/JiHuiYiYou/JiHuiYiYou-compiler](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler)

If the wiki and the repository disagree — **the repository wins**, then file an issue so we can fix
the page.

---

## One document outside this group

[`docs/abis/jhyy-binary-format-v1.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-binary-format-v1.0.0.md)
— the design draft of the JHYY native binary format (`.jhyynb`), **not implemented yet** (ABI §
12.10). No artifact has implemented it so far, so it carries no compatibility promise at all.

---

## What's next

- [Language spec v{{spec_version}}](/compiler/docs/spec.html) — what you must obey when writing JHYY code.
- [ABI v{{abi_version}}](/compiler/docs/abi.html) — how artifacts recognize each other.
- [Standard library](/compiler/docs/stdlib.html) — the function signatures and traps of the {{stdlib_modules}}
  modules.
