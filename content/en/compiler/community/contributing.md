---
title: Contributing
description: The full path from filing an issue to merging a PR
layout: docs
project: compiler
zone: community
---

# Contributing

This page is the full-path version of the repository's [`CONTRIBUTING.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/CONTRIBUTING.md): filing issues, running the gates, writing the PR. **Before you start, work out which tier your change falls into.**

---

## Repository map (short version)

| What you want to change | Where |
|---|---|
| Compiler source + the C bridge | `compiler/src0/` (31 `.jhyy` modules + `jhyy_helpers.c`) — **the only implementation**, there is no second copy |
| Backend | `compiler/src0/codegen_amd64_*.jhyy` (the self-written amd64 emitter) |
| Standard library | `compiler/src0/std/` (8 modules: `mem` / `fmt` / `io` / `math` / `string` / `vec` / `os` / `arena`) |
| Tests | `compiler/tests/examples/` + `regress.py` at the repository root |
| Self-hosting and gate scripts | `compiler/tests/bootstrap/` |
| Language / ABI / binary format contracts | `docs/abis/` |
| Workaround ledger | `docs/internal/workarounds.md` (**never archived**, entries are closed but never deleted) |
| The numbers that change | `docs/internal/FACTS.md` (**the single source of truth**) |
| Plan line | `docs/plans/v4/` (one plan per cell) |
| Cross-project design baseline | `docs/coordination/` (one final version each on the compiler side and the OS side) |

The full version is in the [repository map](/compiler/governance/repo-map.html).

---

## Build and test

The host is **Windows 10 + MSYS2** (`C:\msys64\mingw64\bin\bash.exe`).

```bash
# Dependencies
pacman -S --needed mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-binutils

# Build the compiler (jhyy compiles itself; make iterates the self-hosted closure to a fixed point)
make all           # → compiler/build/bin/jhyy.exe

# Regression suite
python regress.py                       # full suite
python regress.py --tests=hello.jhyy    # a single case
python regress.py --all                 # includes the gated cases
```

> [!IMPORTANT]
> **Do not** use the MinGW `gcc` that comes with Git Bash — it does not support PE+ linking and fails at the link stage.
> **Run all the gates from the repository root**: the scripts resolve paths against the current directory, and running them in a subdirectory reports every file as missing, which looks like drift but is not.

### What each gate covers

| Gate | What it covers | When to run it |
|---|---|---|
| `make` (the self-hosted closure) | The `.s` produced across generations is **byte-identical** | After changing `compiler/src0/*.jhyy` |
| `python regress.py` | The exit code / stdout assertions of every test case | After any behavioural change |
| `python scripts/dev/audit_test_assertions.py --strict` | Every test case has an assertion that **can fail** (zero signal is red) + an instruction-vs-read-point cross-check | After changing tests |
| `bash compiler/tests/bootstrap/artifact_checks.sh` | 20 **artifact checks** — the failure mode lives in the byte layout, not in the program's return value, and a `.jhyy` test cannot catch it | After touching codegen |
| `bash compiler/tests/bootstrap/closure_check.sh` | The `.s` of Stage 2 == the `.s` of Stage 3 (**local gate**, not wired into CI) | After changing `src0` |
| `python regress.py --fixed-point` | N=10 cross-generation `.il` + `.s` are byte-identical (**local gate**) | Release-grade process |
| `bash compiler/tests/bootstrap/artifact_fresh_check.sh` | The `jhyy.exe` committed to the repository behaves the same as the current build | After changing `src0` — otherwise it goes red |
| `python scripts/dev/bump_version.py check` | `VERSION` == every version string in the repository | When you touched the version number or a version string |

### Which one to run before committing

| What you changed | At least run |
|---|---|
| Docs only / tests only | Docs need fact-checking (is the limitation still there? did the sprint that fixes it ship?), CI runs the facts gate; tests need `python regress.py` + the assertion strength audit |
| Changed `compiler/src0/*.jhyy` | `make` + `python regress.py` + `artifact_checks.sh`, and update the self-hosted artifact committed to the repository; add `--fixed-point` if you touched the version number or the release process |

Details are in [Build and test](/compiler/docs/build-and-test.html) and [Build from source and bootstrap](/compiler/download/bootstrap.html).

---

## Change classification and the matching thresholds

### These must be designed first, then implemented

**Language syntax / semantics · ABI and memory layout · Memory model · Stable standard library API · Error code semantics · The self-hosting boundary.**

Rationale: the language spec v4.0.0 and the ABI whitepaper v4.0.0 are both **locked** contracts, appendix B is the formal list of known limitations, and the diagnostic codes are tabulated in the spec — changing any of them affects every program that has already shipped.

> [!NOTE]
> **There is no written-out RFC process yet.** The repository has no RFC template, no numbering rules and no review period — the word `RFC` appears in the repository only in two internet standards (RFC 3629, RFC 4122). The existing substitutes are: the locked-in spec + appendix B, `docs/plans/v4/` with one plan per cell (fixed structure, containing Goal / Scope / acceptance gate / review checklist / Risks), and `FACTS.md` § 4 as the source of truth for scheduling. The [RFC process](/compiler/governance/index.html#rfc) section of this website is the place where this rule is being filled in.
>
> **What to actually do until the rules are complete**: open an issue first to explain the motivation, the scope and the impact on existing code, and wait for the maintainer to decide before you start; do not edit the spec text directly. Which cell of `docs/plans/v4/` it lands in, and what the acceptance gate is, gets written in the plan.

### Small changes

An issue (explaining the problem) + a design note + a PR, with the **design note self-contained in the PR** — do not make the reviewer go and dig through the issue themselves.

---

## Commit and PR conventions

The following four are the original requirements from `CONTRIBUTING.md`:

1. **One PR does one thing.** When the description needs the word "and", it is probably two PRs.
2. **The gates must run.** **A gate that never ran is a gate that never passed.** Every CI job on the PR has to be green — including the **SysV ABI** job: it is the only runner that can actually **execute** those six test cases (`windows-latest` skips them), so it being green does not mean they are covered.
3. **Summarise the change in the commit message**; **if any AI assistant took part in writing the code, add a `Co-Authored-By` trailer**.
4. **If you touched documentation, keep the facts in sync**.

### Changing compiler source = a release-grade process

Changing `compiler/src0/*.jhyy` costs far more than changing documentation: **adding one local variable shifts the module-level temp numbering**, and the self-hosted build drifts with it. So you have to:

- run the full regression suite;
- refresh the self-hosted anchor (`make`, which iterates to the fixed point and installs the new binary);
- **commit the new `compiler/build/bin/jhyy.exe`** — it is a git-tracked artifact, and CI's `artifact-fresh` gate compares it against the current build; a stale one gets caught.

**Changing comments only is free**: the lexer strips comments before codegen, and the compiler binary stays byte-identical.

### Code style

- `.editorconfig`: UTF-8 / LF / final newline / trim trailing whitespace; indentation **4 spaces** (`.jhyy` / `.c` / `.h` / `.py` / `.sh` / `.ps1`), **2 spaces** (`.md` / `.json` / `.yml`), **Makefile uses tabs**.
- On the C side, `-Wall -Wextra` with **zero warnings**.
- **One language per document**: the outward-facing front doors (`README.md` / `CONTRIBUTING.md` / `CHANGELOG.md`) are in English, the only Chinese front door is `README.zh-CN.md`, and `docs/**` inside the repository is in Chinese; no mixing Chinese and English within one document. Chinese uses simplified characters only.
- **The two READMEs have to be changed together** — a forked front door is worse than a stale front door.
- Path references in documentation are written relative to the current file; after changing them, run `python scripts/dev/docs_facts_check.py` (it includes broken-link checking).

### Test layering

The regression suite has 299 cases in total, split into three layers by **signal source**:

| Layer | How it is decided | Cases |
|---|---|---|
| Real assertions | The assertion is written in the test case source | 215 |
| harness-decided · expected compile error | The case declares `// EXPECT-ERROR: "..."` | 56 |
| harness-decided · exit code comparison | The case declares `// EXPECT: N` | 8 |
| SKIP · the case skips itself | The case carries a `// SKIP:` directive | 6 |
| SKIP · library module | A library module with no entry point | 14 |

215 + 56 + 8 = **279** (runnable), plus 6 + 14 = **299** (total).

The test directive set is a fixed group: `EXPECT` / `EXPECT-ERROR` / `EXPECT-OUT` / `XFAIL` / `SKIP` / `SETENV`; new cases use only these.

The assertion strength audit reports the **number of zero-signal cases** — a test that cannot fail is worse than no test at all: it checks nothing yet reports success.

### Signature requirements and backporting

- **Signature requirement: none.** The repository has no DCO and no GPG signing requirement, and GitHub's `web_commit_signoff_required` is off too.
- **Backport rules: not yet written down.** The repository has a single mainline (`main`), no release branch matrix and no backport policy.

---

## Two contribution templates

> [!NOTE]
> **These two tables are not yet in the repository's `CONTRIBUTING.md`** — the original only specifies the PR process and the gates. The requirements in the tables are the project's current practice, published here on the website as templates first; writing them back into the in-repo documentation is under way.

### Teaching contributions (tutorials / lecture notes / samples)

| Required | Notes |
|---|---|
| **A complete, runnable `.jhyy` file** | Not a fragment; the imports and `main_jhyy` cannot be left out |
| **Expected output** | stdout **and** the exit code, both of them |

The best samples are the ones that fit into `compiler/tests/examples/` — then the sample is both teaching material and a regression case.

> [!NOTE]
> **There is no written-out "teaching material directory" yet.** The repository has no place such as `docs/tutorials/`; long-form material currently goes into the Wiki. "Teaching material must ship a runnable sample" is inferred from the regression suite's existing discipline, not a written clause — we are working on it.

### Compiler contributions

| Required | Notes |
|---|---|
| **An IR sample** | The `JHY_WRITE_IL=1` `.il` output, so the reviewer can read the intermediate representation instead of guessing |
| **A regression test** | New `.jhyy` cases go into `compiler/tests/examples/`; when fixing a bug, **write the reproducing case first** |
| **Performance / correctness impact** | Static metrics such as frame size, memory accesses and instruction count, plus "could this change existing behaviour" |

If you changed `compiler/src0/*.jhyy` you must additionally declare that **this is a release-grade change** — the PR template has one field that asks exactly this.

---

## Issue format

Two issue templates (*Compiler bug report* / *Feature request*), and blank issues are allowed too. When reporting a bug, all four of these are required:

1. **A minimal reproducer** — the complete `.jhyy` source;
2. **Actual vs expected output**, **including the exit code**;
3. **The version** — the first line of `jhyy --help` (**there is no `jhyy --version` flag**, it never existed);
4. **The compiler's origin** — a released binary, or a self-hosted build?

> [!WARNING]
> **Take the exit code from the harness or Python `subprocess`, do not read MSYS2 bash's `$?`.** bash truncates the exit code to 8 bits (`value & 0xFF`), so expected codes >= 256 have to be reduced first: 827 → 59, 501 → 245, 300 → 44, 1000 → 232. A lot of "the exit code is wrong" reports are just this.

---

## The issue label system

The labels that **actually exist** in the repository are these thirteen:

| Label | Meaning | Source |
|---|---|---|
| `bug` | The compiler did the wrong thing | Default in the *Compiler bug report* template |
| `enhancement` | Feature request | Default in the *Feature request* template |
| `documentation` | Documentation change | Manual |
| `question` | A question | Manual |
| `good first issue` | Good for newcomers | Manual |
| `help wanted` | Needs extra attention | Manual |
| `duplicate` | Duplicate | GitHub default |
| `invalid` | Not valid | GitHub default |
| `wontfix` | Will not be done | GitHub default |
| `roadmap` | Already on the roadmap | Manual |
| `短期` / `中期` / `长期` | Scheduling tier | Manual, corresponding to the timeline in `FACTS.md` § 4 |

> [!NOTE]
> **There are no `RFC`, `OS`, `backend`, `arena`, `breaking`, `needs-decision` labels yet** — they do not exist in the repository. The planned per-domain label system is being filled in.
> Two more facts about the current state: the `good first issue` label exists, but there are currently **no open tasks carrying it** (the number of open issues is 0); and on the Discussions side there is **no separate label system**.

---

## Next

- [Community home](/compiler/community/index.html) — the channels and the current numbers.
- [Code of conduct](/compiler/community/conduct.html) — the minimum agreement for taking part in this project.
- [Security disclosure](/compiler/community/security.html) — do not post security issues to a public issue.
- Original: [`CONTRIBUTING.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/CONTRIBUTING.md)
