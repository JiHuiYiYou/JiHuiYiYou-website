---
title: Targets and cross-compilation
description: The trade-offs of the four targets, what freestanding means, and the minimal bare metal toolchain
layout: docs
project: compiler
zone: download
---

# Targets and cross-compilation

This page answers four questions: **which targets exist**, what each target produces, **what freestanding actually
changes**, and which tools a bare metal build minimally needs.

---

## Target boundary: amd64 only

There are currently four targets, all of them x86-64. **No aarch64, no riscv64, no wasm.**

| Target triple | ABI | Artifact | Status | Explanation |
|---|---|---|---|---|
| `amd64_win` | MS x64 | PE/COFF executable (`.exe`) | Stable | The host's default target. The compiler itself runs on this target |
| `amd64_sysv` | SysV AMD64 | SysV assembly (`.s`) → linked into an ELF by an external ld | Stable | The artifact is assembly text; the linking is done by the external linker |
| `amd64_win_freestanding` | MS x64 | UEFI executable image (`.efi`) | Under test | The calling convention is byte-identical with `amd64_win`; the UEFI entry path is not finished yet (ABI § 12.8) |
| `amd64_sysv_freestanding` | SysV AMD64 | freestanding assembly (`.s`) | Under test | The main entry target for bare metal kernels; it has the same UEFI entry gap |

All four targets **go through** the self-written amd64 backend (`target_backend_mode` always returns
`BACKEND_SELF`), and there is no QBE fallback path — QBE was removed from the build chain long ago.

> [!IMPORTANT]
> This is **the current boundary**: the compiler itself only has an amd64 backend. The ARM target is being worked on in
> another project — [for-VEX](/vex/index.html) goes with JHYY emitting ARM machine code (`.o`) directly and then linking
> the official SDK into a `.bin`; that route is currently still at the fact-baseline stage, the ARM backend has not been
> started. "Multi-architecture ABI" is an unscheduled item after v4.16 in the release plan.

The ABI side registers this explicitly: § 12.10 "no aarch64 / riscv64", and the `.jhyynb` native binary format
is still a design draft.

---

## What freestanding changes

This is the easiest one to misread. **freestanding only switches the "calling convention ownership + entry hooks",
it does not switch the way things get linked.**

What the link line ends up being is decided by **whether the source file has `#[no_std]`**, not by `--target`
(ABI § 7):

| Source file | Link line |
|---|---|
| No `#[no_std]` | Links `runtime.o` + `helpers.o` (the C runtime bridge) |
| Has `#[no_std]` | Links neither of the two, and adds `-nostartfiles -nodefaultlibs -Wl,--entry=main -lgcc` |

Both branches carry the same string of link flags:

```text
-g0 -Wl,--build-id=none -Wl,--stack,67108864 … -lm -lkernel32 -luser32 -lshell32 -ladvapi32
```

**The Windows system libraries and `-lm` are added unconditionally**, `#[no_std]` not excluded. So a genuinely
freestanding image has to be finished with `lld-link` or a custom link line of its own.

Two practical consequences follow:

- **The output container format is not decided by `--target`**, it is decided by the `ld` of the host toolchain
  (`link_with_gcc` has no target parameter, ABI § 12.9). The PE / ELF in the table are just what each target
  conventionally produces.
- **Targets other than `amd64_win` have to be given `--no-link` explicitly.** Without it the compiler refuses outright:

  ```text
  jhyy: refusing to link a cross target - this build's linker always emits a Windows .exe (via the bundled toolchain).
        Use --no-link, then link the .s with a toolchain that matches the target.
  ```

  That guard has its reason: link SysV assembly with a Windows linker and what comes out **has zero warnings at
  compile time and a runtime error**.

---

## Crossing over to Linux

The `amd64_sysv*` targets produce SysV assembly, which is linked and run on Linux. Three steps in all:

```bash
# 1. on Windows — emit the .s (a cross target must not be linked)
./compiler/build/bin/jhyy.exe compile --target=amd64_sysv_freestanding --no-link prog.jhyy -o prog
#    ⇒ prog.s

# 2. on Linux — link it into a static ELF
gcc -nostdlib -static -T runtime/linux_elf/link.ld -o prog.elf \
    runtime/linux_elf/crt0.S prog.s

# 3. run it
./prog.elf
```

The Linux runtime calls `main_jhyy` (not `main`) and exits with its return value, so the entry convention is the same
as on the hosted side — but the linking is `-nostdlib`, so a freestanding program cannot call libc.

This is exactly the chain CI runs on `ubuntu-latest`.

> [!NOTE]
> **The compiler itself only runs on Windows.** `jhyy.exe` is a PE executable, and the self-hosted closure has to
> execute it; the C-side compiler has been removed, so there is no "build a native ELF jhyy with the Linux gcc" path.
> The **artifacts** are not bound by this.

---

## The minimal bare metal toolchain

To actually build a bare metal image you need at least the following. Checked against JHYY's status item by item:

| Stage | What it needs | JHYY status |
|---|---|---|
| The compiler itself | `jhyy.exe` | The self-hosted anchor, `compiler/build/bin/jhyy.exe` (the repository already has a copy) |
| Assembler | **The self-written amd64 emitter** | The backend emits `.s` in GAS / AT&T syntax directly; there is no standalone assembler binary |
| System assembler | GNU `as` (invoked through `gcc -c`) | Only needed when turning the `.s` into an object file |
| Target linker | See below | An external `ld`, whose container format is decided by the host toolchain |
| `objcopy` / `objdump` | binutils | **Not needed** for compiling itself: `objdump` is only used in the artifact checks to verify by disassembly, `objcopy` shows up on the ARM route of for-VEX (the official SDK ships with it) |
| QEMU | `qemu-system-x86_64` | For running UEFI images, **not** a step of the compile |
| UEFI firmware | OVMF (`edk2-x86_64-code.fd` + `edk2-vars.fd`) | The repository's `scripts/dev/install/install-freestanding-toolchain.sh` copies them out of MSYS2's QEMU share |
| GRUB / limine | None | **Not in the repository**; the main line goes with OVMF + QEMU, and the spike of the OS project uses its own `BOOTX64.EFI` |

**A bare metal build still needs an external ld.** ABI § 7 puts it very plainly: the link line is gcc's as + ld,
`link_with_gcc` has no target parameter, and the output container is decided by the host `ld`. JHYY itself only takes
care of "turning the source into a `.s`"; everything from the `.s` to the executable image is the job of the external toolchain.

Each of the three kinds of target needs its own linker:

| Target | Linker | Command shape |
|---|---|---|
| `amd64_win` | Host gcc → ld (PE) | The compiler links it itself and produces a `.exe` |
| `amd64_win_freestanding` | `lld-link` | `lld-link /SUBSYSTEM:EFI_APPLICATION /ENTRY:efi_main /MACHINE:X64` |
| `amd64_sysv*` | External gcc / ld (ELF) | On Linux, with `-nostdlib -static` and its own `link.ld` |

The complete four steps of the UEFI route are already written as scripts in the repository:

```bash
# 1. jhyy compile → .s
scripts/dev/build/build-efi.sh compiler/tests/examples/hello-freestanding/efi.jhyy
# 2. gcc -c .s → .obj     3. gcc -c efi_helpers.s → .obj
# 4. lld-link → .efi
# Then:
scripts/dev/test/run-ovmf.sh hello-freestanding.efi
```

`lld-link` comes from the `mingw-w64-x86_64-lld` package of MSYS2; `run-ovmf.sh` starts EDK2 with QEMU and grabs
ConOut through debugcon.

---

## Known gaps

The parts of the freestanding side that are not finished are all registered in ABI § 12:

- **§ 12.8 · UEFI EFIAPI wrapper not implemented**: the two hooks of freestanding
  (`emit_entry_point` / `no_crt_init`) are **both empty implementations** — the compiler generates no EFIAPI
  wrapper and does not automatically suppress the CRT / runtime linking. The entry symbol is supplied by the user
  (`efi_main` / `_start`).
- **§ 12.9 · No cross-compilation container backend**: `--target` does not switch the PE / ELF output.
- **§ 12.10 · No aarch64 / riscv64**.
- **§ 12.1 · struct / enum return values unconditionally go through sret on all targets**, with no size threshold;
  this does not match the SysV standard when interoperating across languages.
- **§ 12.6 · Stack slots are only guaranteed to be 8-byte aligned** (there is currently no type with 16-byte alignment, so it is not triggered).

---

## Next

- [ABI v{{abi_version}}](/compiler/docs/abi.html) — the contract itself.
- [Bare metal and kernel development](/compiler/docs/osdev.html) — what it actually takes to write a bare metal program.
- [Build from source and bootstrap](/compiler/download/bootstrap.html) — building the compiler from source.
