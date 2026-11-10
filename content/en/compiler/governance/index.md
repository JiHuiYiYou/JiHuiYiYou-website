---
title: Governance
description: Who decides, how a change gets proposed, how a version ships — and which parts still have no written rules
layout: docs
project: compiler
zone: governance
---

# Governance

This page answers three questions: who has the final say, how a change gets proposed, how a version ships.
The last section lists **the parts that still have no written rules** — for those entries, writing "none"
is better than writing a sentence that sounds mature.

Every rule on this page points at one specific file in the repository. Anything whose source cannot be
found goes into the gap table in the last section.

---

## How decisions are made

JHYY is a **personally maintained pre-1.0 compiler project**. That is a sentence the repository itself
writes at the top of `SECURITY.md`, not rhetoric from this site.

| What is decided | Who decides | Source |
|---|---|---|
| Bug fixes, diagnostic wording, build scripts, toolchain, documentation | The maintainer | The PR flow in `CONTRIBUTING.md` |
| Language syntax / ABI / memory model / stable standard library API / error code semantics / self-hosting boundary | The maintainer, but **a written proposal is required first** | These six items are exactly the scope locked down by the three contracts in `docs/abis/` |
| Version number and release timing | The maintainer | The `VERSION` file at the repository root + `scripts/dev/bump_version.py` |

The only written "proposal format" in the repository is `docs/plans/v4/<version>-plan.md` — one version slot
per cell, with a uniform structure: Context (why this version) · Goal (measurable) · Scope · acceptance
gates · a review checklist at kickoff · Critical files · Risks · Out of scope · References. Every plan
states at the top that "the version number is a reserved number, reviewed against the actual state at
kickoff".

The cross-project design baseline has one more home: `docs/coordination/`, one "final version" on the
compiler side and one on the OS side.

---

## RFC

**The repository currently has no RFC directory and no RFC template.** Verified: under `docs/` there is
no `rfcs/`; the string "RFC" appears in only two places across all the markdown in the repository, and
both mean something else — Unicode code point ranges cite RFC 3629, and installer GUID generation cites
RFC 4122.

So two things have to be kept apart: **which changes should go through the proposal flow** (that judgement
is clear) and **what a proposal should look like** (there is no written template for that yet).

### Which changes require a written proposal first

| Change | Why |
|---|---|
| Language syntax | Spec v{{spec_version}} is locked; the syntax is a contract |
| ABI (type layout / calling convention / struct passing) | ABI v{{abi_version}} is locked; it has to line up across modules and across targets |
| Memory model | The semantics chapter of the spec |
| Stable standard library API | User code depends on it |
| Error code semantics | Diagnostics and exit codes are a user-visible contract |
| Self-hosting boundary (which code is allowed to be written in JHYY) | Decides whether the compiler can keep compiling itself |

These six items correspond exactly to the scope covered by the three documents under `docs/abis/`: the
language spec, the ABI, and the binary format. They are **locked** — locking means a change has to ship a
contract version, not borrow the toolchain's patch digit.

### Which changes can go straight to issue + design note + PR

Bug fixes, diagnostic messages, test cases, build and CI scripts, the installer and the extension, and pure
documentation. The "Which area?" dropdown in `.github/ISSUE_TEMPLATE/feature_request.yml` lists
Documentation / Tooling / Standard library / Target support — those areas have no proposal step in the
repository's day-to-day flow. Adding a **new API** to the standard library belongs to the previous table;
changing the behavioural detail of an existing function belongs here.

### What a proposal should contain

The repository has no template; what follows is a **draft convention** (not the current state):

1. Motivation — what problem is being solved, without the solution
2. Design goals
3. Non-goals (explicitly what will not be done)
4. Syntax / semantics draft
5. Impact on types and IR
6. Impact on ABI and linking
7. Impact on arena and bare metal (freestanding)
8. Alternatives, and why this one was chosen
9. Known defects and limitations
10. Migration path (what it means for existing code)
11. Stability guarantees (which behaviours never change from here on)
12. Implementation staging

### How it is meant to be filled in

Add a `docs/rfcs/` directory to the repository along with a `docs/rfcs/_template.md` whose body is the
twelve items above. The first proposal starts from "the candidate changes for language spec v4.1".

---

## Release

### How the version number goes up

**The single source of truth for the version number is the `VERSION` file at the repository root**; it is
never edited by hand. The current stable release and the historical archive are on the
[download page](/compiler/download/index.html).

Bumping a version takes five steps, and **the order cannot be reversed** (`docs/internal/build.md`
§ version automation). The version number in the commands below is only an example; the real one follows
the schedule at the time:

```bash
python scripts/dev/bump_version.py set 4.1.5   # bump VERSION + the version strings across the repo + create the release note stub + insert the CHANGELOG entry
make                                           # the self-hosted artifact must be recompiled (the version is a string literal in main.jhyy)
pwsh -File installer/build.ps1 bundle          # build
python scripts/dev/bump_version.py finalize    # fill in the sha256 + the measured artifact sizes
python scripts/dev/bump_version.py check       # zero-drift gate
```

The second step cannot be skipped: `make` iterates the self-hosted compiler to a fixed point; skip it and
the compiler you install reports the previous version number.

### What a release contains

A release = a batch of changes landing on some version slot + a tag + a GitHub Release + three artifacts
(the GUI installer EXE / the enterprise distribution MSI / the VS Code extension VSIX) + the body of one
`installer/release-notes/<版本号>.md`.

The change record has two layers, and **this is a convention written down in the repository**:

| Layer | File | Rule |
|---|---|---|
| One line per change, for the outside | `CHANGELOG.md` at the repository root | One line per version; plus one release table (with a tag) and one change slot table (without a tag) |
| Per-version details | `docs/archive/logs/v4/changelog-v4.0.0.md` | **One version axis has exactly one umbrella changelog**; patch versions add a section to the same file and **do not open a new file** |

The umbrella for the v4 axis is already laid out section by section as `## v4.0.1`, `## v4.0.2`,
`## v4.1.4`. The IDE repository's `CHANGELOG.md` opens with the same convention.

### The gates a release has to pass

Every release gate in `release.yml` carries a `# gate:` marker:

| Gate | What it checks |
|---|---|
| `release-version` | The `VERSION` file does not match the tag ⇒ refuse to release |
| `release-ci-green` | On the manual release path, the CI run for that tag has to be a success |
| `release-anchor` | The artifacts from that release build and the one committed into the repository produce byte-identical assembly from the same source |
| `release-build` | Burn bundle + MSI + VSIX build successfully |
| `release-sha256` | `SHA256.txt` matches the artifacts one by one |
| `release-notes` | A placeholder is unfilled ⇒ refuse to release; a missing `installer/release-notes/<版本号>.md` ⇒ fail outright |
| `release-msi` | `wix msi validate` |
| `release-artifacts` | Not one expected artifact may be missing |

Before that, the CI side still has to pass the self-hosting closure, the committed artifact sync, the full
regression, assertion strength, artifact-level assertions, the SysV ABI cross-implementation differential
testing, and other gates — the list is in `docs/internal/FACTS.md` § 2.

**The enforcement point is in the workflow's `needs:`, not in the repository settings.** On the tag path
the release job only starts once the three jobs `build-and-test + vscode-ext + sysv` are all green; the
required status check on `main` is a repository setting on the GitHub side, and `enforce_admins` is off —
administrators can bypass it.

### There are no three channels

The repository has **no nightly / beta / stable release channels**, and no automated pre-release builds.
There are only two kinds of thing: **released releases** (with a tag, with a GitHub Release, with
artifacts) and **change slots** (in the tree, but carrying neither a tag nor artifacts of their own; their
content goes out with the release that follows).

The only "pre-release" form is the RC: the release flow marks an RC tag as a GitHub prerelease —
v4.0.0-rc1 was shipped that way.

The `stable` / `beta` labels on the download page are **target maturity** (how far along a given target
triple is), not release channels.

---

## Contract versions and toolchain versions are two different things

| | Contract | Toolchain |
|---|---|---|
| What it is | Language spec / ABI / binary format | Compiler + standard library + installer |
| Version | Language spec v{{spec_version}} · ABI v{{abi_version}} · binary format v{{binary_format_version}} (**design draft, not implemented**) | v{{site_version}} ({{site_version_date}}) |
| When it changes | Only when the semantics change | It changes with every bug fix |

Language spec v{{spec_version}} and ABI v{{abi_version}} are the contract baseline of the v4 generation, and the lock date
noted at the head of the spec documents is **2026-10-24** — on that day `jhyy-lang-spec-v1.3.0.md` and its
17 v3.x supplements were archived into git history together, because they contradict each other: v1.3.0
documented block expressions that were never implemented, and also documented literals that silently
computed the wrong value.

**Why it is split this way**: change a contract once and the compiler, the user code already being
written, the OS line and the IDE's block syntax all have to move with it. So contracts use their own
version number, and changing a contract ships a contract version; the toolchain's patch digit only carries
things that do not change the semantics. The batch fixed in v4.1.4 — arguments past the 16th being dropped,
SysV stack arguments overwriting the caller's locals, the floating-point stack argument path trampling
callee-saved `%xmm15` — are all implementation defects; they do not change the semantics, so only the
patch digit goes up.

The body of the spec also has one writing rule: **only write the behaviour the code has actually
implemented today**; whatever is not implemented or is restricted goes into appendix B. So the "contract
page" writes the promise, and the "toolchain version" writes how far that promise has been fulfilled — two
things, two version numbers.

Incidentally: `v4.0.0 final` was never promoted (the workaround ledger had not been cleared back then),
and the v4 axis starts from `v4.0.0-rc1`.

---

## What still has no written rules

This is the section of this page that most deserves to be read. Every entry below has been **verified
against the current state of the repository**; none of it is speculation.

| What is missing | Current state | How it is meant to be filled in |
|---|---|---|
| RFC directory and template | The repository has no `docs/rfcs/`, and no RFC template at all | Create the directory + the template; for the body, see the RFC section of this page |
| How RFC reviewers are decided | No rule states "who reviews, how many approvals are needed, how a dissenting opinion is settled" | Set one minimal rule in `docs/rfcs/README.md`: a proposal that touches the three contracts needs the maintainer's written consent + one independent review |
| CODEOWNERS | **None of the four repositories has a CODEOWNERS file** | Write one per directory: contract documents, the workaround ledger and CI workflows point to the maintainer; the remaining directories point to contributors |
| Release owner | There is no second role. `SECURITY.md` describes itself as "maintained by one person" | In the short term the maintainer takes it on; once there is a second person who can run the release chain independently, write down a rotation rule |
| Trademark policy | The repository has **no trademark / logo usage policy file at all** | Write `TRADEMARK.md`: allow descriptive uses, forbid suggesting official endorsement, forbid modifying the logo |
| Branch protection and merge rules | No written requirement. `docs/internal/build.md` records one fact: `enforce_admins` is off, so administrators can bypass the required status check on `main` | Make "run the gates yourself before merging" a documented requirement, and turn `enforce_admins` on on the GitHub side |
| Cross-repository coverage of the code of conduct | The compiler repository has `CODE_OF_CONDUCT.md`; **IDE / OS / for-VEX do not** | Add one to the latter three, or state explicitly "the compiler repository's version governs" |
| Cross-repository coverage of security disclosure | The compiler and IDE repositories have `SECURITY.md`; **the OS and for-VEX repositories do not** | Add a minimal version to the latter two, or state that they go through the compiler repository's private channel |
| for-VEX's license | **The for-VEX repository has no LICENSE file at its root** — the only one of the four | Add the same MIT as the other three (`Copyright (c) 2026 JHYY`) |
| Contributor agreement (CLA / DCO) | No requirement | Do not introduce one for now. If one is introduced, first write down clearly "what happens to historical PRs after it is introduced" |
| i18n policy | None | The site starts monolingual (Chinese); the English version opens once someone is maintaining it long-term |

**Why these are written out**: the thing that most often goes wrong in a small team is not "the rules are
not strict enough" but "the rules point at a person who does not exist". Every one of the above has to name
**who is responsible** when it is filled in — otherwise it goes stale after a few months. Better to let the
community page admit what it is missing than to write out a system that looks complete and that nobody
actually executes.

---

## Related

- [License](/compiler/governance/license.html) — the exact terms of MIT and the licensing status of each repository
- [Repository map](/compiler/governance/repo-map.html) — what each of the four repositories is responsible for
- [Contributing guide](/compiler/community/contributing.html) — the concrete steps for filing an issue and opening a PR
