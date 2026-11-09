---
title: JHYY IDE
description: A desktop workbench where block programming and text editing share one AST
layout: page
project: ide
zone: ide
---

A desktop IDE for JHYY: **drag blocks, write code, talk to Claude Code on your own machine**.
A VS Code-style workbench: two coding views share one AST, and diagnostics always come from a real `jhyy.exe`.

## Three panels

- **Text view** — CodeMirror 6, just write code. Syntax highlighting, bracket matching, auto-close, indentation, completion (keywords, types, {{stdlib_modules}} standard library modules), and hover hints that give you the **spec section number**. Files open in tabs, and opening a second one does not evict the first; the little black dot is computed from content, so it disappears on its own once you undo back to the last saved version.
- **Block view** — Blockly 13, drag blocks to write programs. The first screen of the toolbox is "Getting started": functions, print, call, number/string, variables, return — plus ready-made **C function declaration** blocks (`printf` / `puts` / `malloc` / `free` / `exit`, with the parameter list filled in for you) — so the first line of every JHYY program no longer has to be typed by hand through the "raw code" escape hatch.
- **Claude Code** — an embedded chat panel in the right sidebar, driving the **already-installed `claude` CLI** on your machine (streaming mode over stdin, with the multi-turn context kept). Claude is wired to the jhyy MCP server, so it can call `jhyy_check` and get diagnostics from the **real compiler** instead of guessing. The sidebar also has a "read-only" switch; when it is on, the system prompt states explicitly that the user has asked you not to modify any files.

There is also a panel at the bottom that is **collapsed by default**: "Check" jumps to the **Problems** page, "Run" jumps to the **Terminal** page.

## The most convincing one: blocks and text share one AST

The two coding views are **two projections of the same tree**, not two separate code generators:

- **Blocks → text** follows in real time (the whole source is regenerated and replaces the text view; the cursor is mapped back to its old position by longest common prefix/suffix).
- **Text → blocks** is rebuilt when you switch back to the block view (rebuilding the blocks on every keystroke makes the canvas shake too much to use).

The AST lives in `src/lang/` and is **pure TypeScript** — no dependency on Electron / Node / Blockly, so the parser, the printer and the block converter can all be unit-tested in plain Node. The IDE's own lexer (73 token kinds) and grammar (57 node kinds) follow the compiler repo's `compiler/src0/`.

**Syntax that blocks cannot express does not silently disappear.** Generics, turbofish, closures, pointers, borrows, slices, `defer`, `asm!`, attributes — these land in an **opaque block** that holds the original source text. You can move it, delete it; as long as **you** do not touch it, that part of the code round-trips byte-for-byte without loss.

And one more rule: **the referee is always the real compiler**. The IDE never guesses whether a program is right; it runs `jhyy.exe`, parses its `file:line:col: error: …` output and shows you the compiler's own diagnostics. One "check" is recorded at about 185ms in the repo README (it uses `--no-link` to skip linking).

## Blocks and text never occupy the screen at the same time

The block canvas fills the whole editing area and the code editor disappears entirely — switch with the block button in the title bar, `Ctrl+Shift+B`, or the command palette. Both sides **keep their state** across the switch: the canvas keeps its zoom and pan, and the editor keeps its undo history and cursor position.

## The bottom panel: Problems + Terminal

- **Problems** — the compiler's diagnostics; click one to jump straight to that line and column.
- **Terminal** — a real shell (MSYS2 bash by default; PowerShell and `cmd` can be selected), and you can open more than one. The terminal prefers a **real PTY** (node-pty / Windows ConPTY); when node-pty cannot be installed it falls back to pipes, and then full-screen TUIs like `vim` and `top` do not run — and when it falls back the status bar shows a badge, so it never silently turns fake. "Run" runs in **the terminal you are currently looking at**; when it finishes the terminal is still alive and the prompt comes back.

> The README still lists three tabs: "Problems / Output / Terminal". **The "Output" tab has been removed in the in-development version** — compiler output and program output now both go to the terminal, the same way VS Code does it.

## Keyboard shortcuts

The menu bar, the command palette and the keyboard shortcuts are three views of **one command table** (`src/renderer/commands/registry.ts`), so a shortcut shown in the menu is always one that really works.

- `Ctrl+Shift+P` — command palette
- `Ctrl+Shift+B` — toggle block view / text view
- `Ctrl+Shift+D` — check
- `F5` / `Shift+F5` — run / stop
- `Ctrl+J` — show/hide the bottom panel
- `Ctrl+Shift+M` — problems
- Terminal — `Ctrl` plus backquote; new terminal — `Ctrl+Shift+Backquote`
- `Ctrl+Alt+B` — show/hide the chat sidebar; `Ctrl+Alt+I` — focus the chat
- `Ctrl+S` / `Ctrl+O` / `Ctrl+Shift+S` — save / open / save as
- `Ctrl+,` — settings

## Consistency gate: {{ide_gate_pass}}/{{ide_gate_total}}

The IDE's parser and printer must say the same thing as the **real compiler**. That is guaranteed by the compiler repo's own example programs — the corpus is the compiler repo's `compiler/tests/examples/` (it grows together with the compiler). Dropping the library files with no entry function, the ones carrying `SKIP` / `XFAIL` directives, and the ones whose name starts with `_` (environment-dependent / need manual preparation), what enters the gate is **{{ide_gate_pass}}** cases — that is the full-coverage number in the IDE repo's CI.

Two gates:

1. IDE parses → IDE prints → the **real `jhyy.exe`** compiles it (with `--no-link`, skipping the link step);
2. then it is **actually run once**, compared against the `// EXPECT:` directives in the source.

The corpus rule is the same as the language repo's own rule: **files starting with `_` do not enter the corpus** — those are environment-dependent / manually prepared repro cases. The full {{ide_gate_pass}} take about 25 minutes to run; by default only one representative subset is run.

## Version status (there is an inconsistency here; stating it plainly)

- `package.json` says **{{ide_version}}**;
- the **badge at the top of the repo README still says v0.1.0** — the badge has not caught up;
- the installer left behind in the local `release/` directory is also still the **0.1.0** one (a build leftover, not a release channel).

On GitHub Releases, **v0.1.0, v0.2.0 and v{{ide_version}} have all been released**, each with one NSIS installer and a `SHA256.txt`. So: **what is released is v{{ide_version}}**; and the top of `CHANGELOG.md` still has an "Unreleased" section (the terminal rework, the settings dialog, and so on) — **the source tree is ahead of every released version**.

To install, go to the repo's [Releases page](https://github.com/JiHuiYiYou/JiHuiYiYou-IDE/releases).

## Platform and prerequisites

- **Windows x64** — this is the only platform currently built and verified; Linux / macOS are not built.
- **Node.js 20+** (development uses 24).
- **A JHYY compiler** — the IDE **does not contain** a compiler; every compile and every diagnostic comes from a real `jhyy.exe`. It looks for one in this order: the path configured in the IDE's settings → the environment variable `JHY_EXE` → `../JiHuiYiYou/compiler/build/bin/jhyy.exe` (the development build in the sibling repo) → `C:\Program Files\JHYY\bin\jhyy.exe` (the official install) → a `jhyy.exe` on `PATH`.

The installer **has no code signature**, so Windows SmartScreen will stop you once; choose "More info → Run anyway".

## Documentation

- **[Wiki](https://github.com/JiHuiYiYou/JiHuiYiYou-IDE/wiki)** — the long-form guide: getting started, architecture, the block subset, Claude Code, troubleshooting, how to add a new block, how to contribute (bilingual, 7 pages).
- [`docs/blocks-subset.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-IDE/blob/main/docs/blocks-subset.md) — which syntax has blocks, which does not, and why.
- Repository: <https://github.com/JiHuiYiYou/JiHuiYiYou-IDE> (MIT license)
