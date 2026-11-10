---
title: Community
description: Where to ask, how to contribute, and the current status numbers
layout: docs
project: compiler
zone: community
---

# Community

This page answers three things: **where to ask questions**, **how each kind of contribution gets in**, and **what this project's numbers are right now**.

First, the situation as it stands: this project is led by **a single maintainer**, and everything listed below is a channel that really exists, not an imagined community structure. There are few channels and few people — that is a fact, not false modesty.

---

## Where to ask

| What you want to do | Where | Notes |
|---|---|---|
| Ask "how do I write this in this language" | [GitHub Discussions](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/discussions) | The categories are GitHub's default six: Announcements / General / Ideas / Q&A / Show and tell / Polls |
| Report "the compiler did the wrong thing" | [GitHub Issues](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/issues) → *Compiler bug report* | The template asks for a minimal reproducer, actual vs expected output, the version, and the exit code |
| Request "I want this feature" | Same as above → *Feature request* | The template first asks **the problem you want solved**; the proposal may be left empty |
| Propose a change | [Pull requests](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/pulls) | Follow the [contributing guide](/compiler/community/contributing.html) |
| Report a security issue | **A private advisory** — do not open a public issue | See [security disclosure](/compiler/community/security.html) |
| Chat casually, ask about progress | QQ group **429807125** | Search for the group number to join |
| Email | **15901598712@163.com** | The fallback channel for code of conduct reports and security reports |

The repository also has a **Wiki** (for long-form writing) and **Projects** (project boards). Issues also allow a blank issue — the templates are guidance, not a gate.

> [!NOTE]
> The Discussions channel is open, but there are no posts in it yet. It is a channel that has just started; the first person to explain a question clearly will save a lot of trouble for everyone after them.

---

## The status numbers right now

What follows are **numbers that change**. The single source of truth is the repository's `docs/internal/FACTS.md`; the website's copy is in `tools/siteconfig.py`.

| Metric | Value | Source |
|---|---|---|
| Self-hosted closure | `make` iterates to a fixed point; the `.s` produced across generations is **byte-identical** | FACTS § 2 |
| Regression suite | **{{regress_pass}} PASS / {{regress_failed}} FAIL / {{regress_skip}} SKIP** ({{regress_total}} in total) | FACTS § 2 |
| Assertion strength | {{assertions}} real assertions, **zero-signal cases 0** | FACTS § 2 |
| Artifact checks | {{artifact_checks}} | FACTS § 2 |
| Workaround ledger | {{workarounds_total}} entries: **ACTIVE {{workarounds_active}}** / DEFERRED {{workarounds_deferred}} / RESOLVED {{workarounds_resolved}} / SUPERSEDED {{workarounds_superseded}} / INVALID {{workarounds_invalid}} | FACTS § 3 |
| Host platform | **1** (Windows x64) | build.md |
| Target triple | **{{targets_count}}** (2 stable / 2 beta) | FACTS § 5 |
| License | MIT | `LICENSE` at the repository root |

**The boundary of each of these numbers** — do not read past it:

- "Byte-identical across generations" proves **generation determinism**, not semantic correctness. A deterministic but wrong compiler can close the loop perfectly too — this is the classic trusting trust gap, and the regression suite gate is what covers it.
- "ACTIVE 0" means there are **no registered** unfixed compiler bugs; it is not proof that "bugs do not exist". The ledger is public and anyone can check it: [`docs/internal/workarounds.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/workarounds.md).
- The {{regress_skip}} SKIP in "{{regress_pass}} PASS / {{regress_skip}} SKIP" are cases carrying a `// SKIP:` directive and library modules with no entry point — not "runs that failed and got skipped".

---

## How to contribute

The four kinds of contribution have different entry points and different thresholds. First work out which kind your task falls into, then read the matching requirements.

### Compiler changes

Entry point: the [contributing guide](/compiler/community/contributing.html). The highest threshold, and the most valuable — because the compiler is self-hosted, changing `compiler/src0/*.jhyy` shifts the self-hosted anchor. **Required**: an IR example (the `JHY_WRITE_IL=1` `.il` output), new regression cases, and a description of the performance and correctness impact.

### Documentation

Entry point: also a PR. Threshold: the change **still has to be fact-checked** — is that limitation still in place? Did the sprint that fixes it really ship? A wrong document is worse than an outdated one. Every number that changes lives only in `FACTS.md`, and all other documents reference it; documentation changes are also cross-checked against CI's facts gate.

### Teaching material

Entry point: tutorials, lecture notes, sample code. Threshold: **a complete, runnable `.jhyy` file plus the expected output (stdout and exit code) is required**. The best samples are the ones that can go straight into `compiler/tests/examples/` as a regression case — then the sample is both teaching material and a test.

### OS and bare metal

Entry point: the cross-project design baseline in `docs/coordination/` (one final version on the compiler side and one on the OS side) is the only basis that crosses the boundary; read it before changing OS-related design. Threshold: for the bare metal and kernel development path, see [Bare metal and kernel development](/compiler/docs/osdev.html).

---

## The plain truth about "community"

As of 2026-11-08, the repository has accumulated **9 issues and 8 PRs, all submitted by the maintainer and all closed**; the number of open issues right now is **0**, with 8 stars and 0 forks.

This is not meant to discourage you. What it means:

- **Your issue will not be drowned out** — there is no queue to wait in.
- **But there is also no second person to review for you.** PR review is currently done by the maintainer alone, and the feedback cycle depends on how their day goes; we are not going to invent a fake SLA for that.
- The maintainer has a clear response target for **security issues** (see [security disclosure](/compiler/community/security.html)); for **ordinary issues and PRs** there is currently no written response deadline — we are working on that one.

The least-effortful way to take part in this project is to get your question clear in [Discussions](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/discussions) first, then decide whether to write it up as a PR.

---

## Next

- [Contributing guide](/compiler/community/contributing.html) — the full path from opening an issue to merging a PR.
- [Code of conduct](/compiler/community/conduct.html) — the minimum agreement for taking part in this project.
- [Security disclosure](/compiler/community/security.html) — reporting security issues, and the known trust boundaries.
- [Repository map](/compiler/governance/repo-map.html) — who owns each directory.
