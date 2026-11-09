---
title: JiHuiYiYou-for-VEX
description: Letting JHYY run directly on the VEX V5 Brain — a measurement-first embedded target route
layout: page
project: vex
zone: vex
---

Adding an **embedded target** to JHYY: the VEX V5 Brain. The current progress is **step 0 complete** —
every unknown on the VEX side has been turned into a measured value and written down as a fact baseline.

## Target hardware

VEX V5 Brain: ARM, **Xilinx Zynq** (Cortex-A9 + FPGA), with VFPv3 + NEON.
DDR base address `0x03800000` (`ps7_ddr_0_S_AXI_BASEADDR` in `lscript.ld`), entry pinned at `0x03800020`.

## Route B is "JHYY emitting ARM machine code directly"

Not "translating it to C++". But the boundary has to be spelled out — **what gets replaced is clang's place;
`ld` and everything below it stay as they are**:

- **Route A** (step 0, the golden reference): JHYY → C source → clang → `.bin`
- **Route B** (the goal): JHYY → ARM machine code (`.o`) → the official SDK → `.bin`

Route B emits an ARM `.o`, then links the official SDK's `lscript.ld` / `stdlib_0.lib` / `libv5rt.a`, and finally
objcopy produces the `.bin`.

This is **isomorphic** to what pros-rs did back then (Rust emits an `.o`, links libpros) — the same route, except
that it **walks it again with measurements**, without carrying that sunk cost.

⇒ The corollary is the same: **the ABI must be locked** (softfp), **the entry point must be locked** (symbol name
`main`), **the binding surface must be locked** (each `extern fn` corresponds verbatim to one C symbol) — whichever
library you link against, that library's ABI is the one you get. If those three cannot be locked, the two routes
cannot be cross-checked against each other.

## Day 0 is complete: the fact baseline

[the fact baseline document](https://github.com/JiHuiYiYou/JiHuiYiYou-for-VEX/blob/main/docs/00-%E4%BA%8B%E5%AE%9E%E5%9F%BA%E7%BA%BF.md)
is the **single source of truth** for the "numbers and platform facts that may change" of this project. Measurement
date **2026-11-08**, machine **Windows 10 + MSYS2**, and every measurement method was a local one (compile /
disassemble / `readelf` / `nm`), with **zero JHYY variables**. Every entry that was not measured is marked
"to be measured"; no guessed values are written down.

The spec has to cover eight things, none of them optional — **seven have conclusions, one is still to be measured**:

- Artifact format and signature layout — measured
- What `vexStartup` does for you — measured (disassembly + relocations)
- Symbol mangling rules — measured (1404 C++ mangled symbols vs the plain C API)
- The softfp / hard decision and its rationale — **locked to softfp**
- The C alignment for passing a struct by value — measured (layout + register convention + the one struct passed by value)
- The minimal binding surface — the exact function names verified, plus a list of the verbatim JHYY-side counterparts
- Where to read the field control state — `vexCompetitionStatus` / `vexCompetitionControl`
- The message pump tick rate — **to be measured** (needs the real robot)

Some measured conclusions:

- **The artifact format needs no extra converter** — the SDK's `objcopy` emits the final format directly. The first
  32 bytes are `XVX5` + version 1, and the entry point follows right after at `0x03800020`.
- **The startup chain is fully closed**: clear `.bss` → stdlib version check → newlib impure data →
  `__libc_init_array` → `vexMain` → `__libc_fini_array`.
- **The user's `main` is a task**, not the main thread — the SDK registers it with the VEXos scheduler via
  `vexTaskAdd(main, 2, "MAIN")`. So Route B **must emit an unmangled `main` symbol**.
- **The ABI is locked to softfp** — neither our ELF nor `libv5rt.a` carries a `Tag_ABI_VFP_args` tag, and the ARM
  ABI default is the base standard variant.
- **The instruction set is ARM state, 4 bytes fixed-length** ⇒ the backend does not have to do Thumb-2 variable-length
  encoding.
- **Two API layers**: the C++ `vex::` (1404 mangled symbols, **not touched**) and the **plain C `vex*()`** — the
  latter is what JHYY's `extern fn` binds to directly, with a **zero-glue layer**.
- **Measured struct layouts**: there are both packed and non-packed ones; in the C API there is **exactly one**
  struct passed by value (`V5_DeviceVisionRgb`, ≤4 B ⇒ passed in registers), everything else is passed by pointer.
- **Memory budget**: 1 MB of heap, 14 KB of stack — recursion depth is a hard constraint.
- **Hard constraints on the JHYY side** (ABI v{{abi_version}}): no variadic calls, no struct passed by value across
  an FFI boundary, and the **pointer width is locked at 64 bits** ⇒ the ARM target must first set the pointer width
  to 4 bytes, or even `extern fn` will not line up.

## Three pitfalls (all of them explicitly warned about in the source documents)

1. **The `objdump` that ships with MSYS2 is x86-only** — on VEX artifacts it reports
   `can't disassemble for architecture UNKNOWN!` ⇒ **you must use `arm-none-eabi-objdump`** (installed separately
   for this round, binutils 2.47). `readelf` reads both.
2. **The SDK's clang is 8.0.0**, its flags say `-target thumbv7-none-eabi` (a **Thumb** target), but the measured
   entry point holds **ARM state** instructions (`e59f00a0` is an ARM state LDR literal; Thumb-2 would be `f8df`).
   This combination of "the target says Thumb, the measured artifact is ARM" depends on the codegen behaviour of a
   specific version — **changing the clang version means re-measuring**; this conclusion cannot just be carried over.
3. **The measurement environment is Windows 10 + MSYS2** — the toolchain paths, the shell and objcopy's behaviour
   are all bound to this environment.

## Schedule ahead

- **Day 0** — done. Hand-written C probes, zero JHYY variables, a purely manual walk through
  `source → ELF → signed bin → program.bin`. The probe also incidentally built a layer over the binding surface
  itself: the display API is entirely variadic, and JHYY does not support variadic calls, so a **non-variadic
  wrapper** `jhyy_vex_display_puts` was added — the variadic part happens only inside C.
- **Day 1–2** — not started. The emitter emits **C** (not C++), the minimal subset plus the minimal binding
  surface (for now binding only `vexDeviceGetByIndex` / `vexDeviceMotorVelocitySet` / `vexDelay` /
  `jhyy_vex_display_puts`).
- **Day 3** — not started. A behavioural comparison of the Route A artifact against the existing C++ project,
  filling in the "to be measured" items left over from Day 0, and finalizing the spec.
- **Stage B** — not started. JHYY's ARM backend.

First, the comparison criteria for Day 3: **"consistent" means behaviour, not bytes**. Routes A and B are two
different code generators (the `.s` will necessarily differ, and the `.o` section layout may differ too), so the
five layers of artifacts — `.s` / `.o` / ELF / `.map` / `.bin` — are **each their own diagnostic evidence**, not
objects for a byte-identical comparison; comparing layer by layer only serves to **locate** which layer the
inconsistency happens in.

Day 0 also has one **acceptance line** not passed yet: **the `.bin` produced by Route A must actually have spun a
motor on a Brain**. That needs a microSD card and a robot — the real-machine behaviour of the display and the
motors, the message pump tick rate, and the coordinate semantics of `vexDisplayPrintf` are all still marked
"to be measured".

The Day 0 probe is reproducible (the artifacts are kept locally and are not in the repository):

```bash
scripts/build-vex.sh spike/day0-c day0c
```

## Boundaries and discipline

- **Do not modify the JHYY main repo directly** — the experiments happen in this repo; once there are measured
  values they land in the main repo and get a review of their own.
- **The output of step 0 is knowledge, not code** — the emitter is a probe, and it is not allowed to grow into a
  product.
- **Artifacts are kept locally and are not in the repository** — the `.bin` / ELF contain code from `libv5rt.a`
  (VEX proprietary); before the "SDK redistribution" question is settled they do not go into a public repo; they
  are kept through **local copy + reproducible script + hash manifest**.

Repository: <https://github.com/JiHuiYiYou/JiHuiYiYou-for-VEX>
