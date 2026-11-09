---
title: JiHuiYiYou-OS
description: An operating system written in JHYY — a measurement-first route that starts from a UEFI boot spike
layout: page
project: os
zone: os
---

An operating system written in JHYY. **It is at a very early stage** — the repo contains only a UEFI x64 boot spike,
and the design baseline is being rebuilt. This page describes **the current state**, not a blueprint.

## What is in the repo right now

The repo currently has one directory, `spike/` (plus an MIT-licensed `LICENSE`):

- `spike/boot.s` — the UEFI x64 bootloader, in Intel syntax.
- `spike/BOOTX64.EFI` — the compiled output of that source file.
- `spike/esp_root/EFI/BOOT/BOOTX64.EFI` — the boot file inside the EFI partition image.
- `spike/wrap_gpt.py` — wraps a raw FAT image into a GPT disk image with **one EFI System Partition** (it writes the protective MBR, the primary/backup GPT headers and the CRC32s itself, and also rewrites the FAT BPB's hidden sector count to the partition's starting LBA).

The most recent commit (2026-10-30) is exactly **"clear the existing design documents — rebuild the design baseline"**:
in one go it deleted the 17 v0.0.x design documents under `docs/`, the 9 external research archives under
`deep_research/`, plus `README.md` and `CLAUDE.md`. Those documents were written in the compiler's v1.8.3 era
(C host + QBE + ABI v{{legacy_abi_version}}), and many of their conclusions have been overturned or are out of date.

The content is not lost — **it is all in the git history**: `24589bd` is the last state before the deletion, and
`git show 24589bd:docs/<file>` will take you back there. The cross-project design baseline now lives in a single
place, in the compiler repo's `docs/coordination/`.

## The four things the spike has actually measured

The header comment of `spike/boot.s` lists the four things this spike is meant to verify:

1. **UEFI x64 hands over directly in long mode**, with no mode-switch assembly needed.
2. **The EFI calling convention is MS x64**: at the entry point `RCX` = the first argument (ImageHandle),
   `RDX` = SystemTable.
3. **The ConOut function pointer is usable via `[protocol + offset]`** — but the offset is **+64, not +80**.
   +80 is **StdErr**; OVMF's ConSplitter does not register StdErr for the graphical console, so writing to it
   only reaches the serial port and is **invisible** on the GOP framebuffer. This +64 / +80 pair was found by
   measurement; the code comment marks it CRITICAL.
4. **The `isa-debug-exit` port `0xf4` can hand an exit code to QEMU**.

> Honest note: the `boot.s` in the current commit ends in an `hlt` infinite loop — it prints `HELLO` / `OK` on
> screen for a human to look at, and the comment says to replace it with `out 0xf4, al` for automated
> verification. In other words, the fourth point has **a place in the code**, but this commit takes the
> human-facing path.

What the spike actually does is three steps, all of them calls through the ConOut protocol's function pointers:
**ClearScreen** (offset 48, which first wipes TianoCore's boot splash), **SetAttribute** (offset 40, white text
on bright red background `0xCF`), **OutputString** (offset 8, prints `HELLO` and `OK`). The header comment marks
this spike as **P0-1** — it is the first point to verify on the OS line, not a small piece of a product.

## Building

The comment in `boot.s` gives exactly this (pasteable):

```bash
x86_64-w64-mingw32-gcc -nostdlib -Wl,--subsystem,10 \
  -Wl,-e,efi_main -Wl,--image-base=0x10000 -o BOOTX64.EFI boot.s
```

`--subsystem,10` means EFI application, `-e,efi_main` sets the entry point.

Put the built `BOOTX64.EFI` into `esp_root/EFI/BOOT/`, and then `wrap_gpt.py` wraps the partition contents into a
bootable GPT disk image.

## Direction (not yet written up as the OS repo's own design document)

The following is **direction**, not a frozen implementation plan:

- **Capability microkernel + `Cap<T>` capabilities** — the compiler repo's
  ["JHYY OS-side design, final version"](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/coordination/JHYY_OS%E4%BE%A7%E8%AE%BE%E8%AE%A1%E7%BB%88%E7%89%88.md)
  locks the kernel identity to "capability microkernel (long term) + privilege layering (first version)", because
  the three specs (language spec v{{spec_version}} / ABI v{{abi_version}} / binary format v{{binary_format_version}})
  already provide a complete authorization chain: object classification `type_tag`, cap authorization
  `rights`/`depth`, in-place cap transfer over IPC — going with a traditional hybrid kernel would turn that
  binary format into decoration.
- **lang-debug ABI** — the "Debug ABI" in
  [language spec § 19](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md)
  is a cross-project contract: settled sizes, the type representation on the `jhyy` side, the compiler emitting no
  DWARF debug info, and FFI boundary reminders.
- **GUI** — the object skeleton (`compositor` / `surface` / `seat` / `buffer`) is enough to build a double-buffered
  display pipeline, but **a complete desktop has not been specified**.

That design document also **lists** the questions the first architecture freeze should answer (whether threads and
address spaces are separated, whether kernel objects share a uniform header, whether revoke is synchronous, whether
interrupts are capabilities, whether a page fault belongs to the kernel or to a user pager, …) — they do not have
answers yet. The `.jhyynb` capability launch format itself is still a **design draft, not implemented**.

In the schedule, the whole OS line (the **OS-1 … OS-16** sixteen version slots in the compiler's
[`docs/internal/FACTS.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md) § 4.3)
is planned for the compiler's v4.6 → v4.15, and **not one of them has started**.

If you want to read the old design drafts (written in the v0.0.x era, against a C host + QBE + ABI
v{{legacy_abi_version}} background, most of their conclusions overturned), the archaeology command is:

```bash
git show 24589bd:docs/README.md
```

## The language side

The language features a kernel needs are already on the JHYY side: `#[no_std]`, freestanding targets, `#[naked]`,
`#[link_section]`, `volatile`, inline `asm!`, and memory barriers. For how to use them to write freestanding
code, see [Bare metal and kernel development](/compiler/docs/osdev.html "Chinese only").

## Summary of the current state

- The repo has **only** one directory, `spike/` — a UEFI bootloader that can print `HELLO`.
- The design documents have been cleared for a rebuild; the roadmap is still to be rewritten.
- There is nothing to install or run, and no release channel of any kind.

Repository: <https://github.com/JiHuiYiYou/JiHuiYiYou-OS>
