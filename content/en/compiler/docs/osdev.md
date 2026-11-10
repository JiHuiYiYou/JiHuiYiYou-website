---
title: Bare metal and kernel development
description: freestanding targets, no_std, inline assembly, and the minimal kernel boot path
layout: docs
project: compiler
zone: docs
---

The question "can I use it to write a kernel" has to be split into three layers for
JHYY: the **language layer**, the **runtime layer**, and the **ABI layer**. Each layer
handles its own business; collapsing them into a single phrase like "no standard
library" leads to the wrong conclusion. This page keeps the three layers apart, then
goes through the "minimal kernel boot path" item by item to check what really works
and what is still empty.

One-line preview: **the parts of the language layer are basically all there; the
runtime layer and the link layer are not wired up yet.**

---

## 1. Three layers to keep apart

| Layer | Switch | What it governs | What it explicitly does not govern |
|---|---|---|---|
| **Language layer** | The `#[no_std]` attribute in the source file | Declares "this module does not want the C runtime", and swaps the entry symbol to `main` | It does not decide the calling convention, and it does not decide the linker |
| **Runtime layer** | The `_freestanding` suffix in the target name | The target shape of "no operating system runtime" | **It does not switch the linking mode** |
| **ABI layer** | `--target=<triple>` | Which calling convention to use (MS x64 / SysV AMD64) | It does not switch PE / ELF output (that is decided by the host `ld`) |

ABI § 1 says it outright: **the two freestanding targets only switch "calling-convention
ownership + entry hook"; they do not switch the linking mode.** In other words,
`--target=amd64_win_freestanding` has a register convention **byte-identical** to
`amd64_win`; the difference lies elsewhere (see section 2).

---

## 2. The link line is decided by `#[no_std]`, not by `--target`

| Does the source file have `#[no_std]`? | Link line |
|---|---|
| No | Links `runtime.o` + `helpers.o`, then unconditionally appends `-lm -lkernel32 -luser32 -lshell32 -ladvapi32` |
| Yes | `-nostartfiles -nodefaultlibs -Wl,--entry=main -lgcc`, and **does not** link the runtime / helpers |

The `--entry=main` in the second row is there because codegen emits symbols
**verbatim** by function name — the user's `fn main` is `main`. A `#[no_std]` module
must define `fn main`, otherwise sema reports
`error: #[no_std] module must define 'fn main()'`.

Note that the second row **still unconditionally appends** `-lm -lkernel32 -luser32
-lshell32 -ladvapi32` at the end. ⇒ A real UEFI / bare metal image **cannot** use this
link line; you have to do it yourself with lld-link
(`/SUBSYSTEM:EFI_APPLICATION /ENTRY:efi_main`) or with a custom link line.

### A pitfall that was once measured (fixed in v4.1.5)

The `#[no_std]` link-line branch is passed down through a side-file flag, and **the
path of that flag file used to be relative to the current working directory**:

- Running `jhyy compile ns.jhyy` at the root of the compiler repository ⇒ takes the
  no_std link line ⇒ the link succeeds, the program returns 42, and the process exit
  code is 42.
- Running the same command anywhere that has no `compiler/build/obj/` subdirectory ⇒
  the flag file cannot be written ⇒ **it falls back to the hosted link line** ⇒ the
  link fails (`collect2.exe: error: ld returned 5 exit status`), exit code 1.

This is not by design; it is a side effect of the path being relative to the CWD. It
is written down here because it is easy to misread as "`#[no_std]` does not compile".

**v4.1.5 fixed it**: the side-file became an **absolute path under the operating
system's temp directory** ⇒ it can be written from any working directory, and no
temporary files are dropped into the user's source tree anymore. A failure on the write
side is now **loud** (the compiler no longer produces an artifact whose "feature
silently stopped working"). Ledger entry W-224 also added an artifact check,
`no_std_any_cwd` — it **runs from a different CWD**: this bug was already invisible to
every existing gate, because they all "run at the repository root".

---

## 3. Known gaps (honest disclosure)

| Gap | Status |
|---|---|
| **The UEFI EFIAPI wrapper is not implemented** (ABI § 12.8) | The `emit_entry_point` / `no_crt_init` hooks are **both empty implementations** ⇒ the compiler generates no wrapper and does not automatically suppress the CRT / runtime linking. The entry symbol is supplied by the user |
| **A real bare metal link line** | Cannot be done — see section 2 (the Windows system libraries are appended unconditionally) |
| **Linking cross targets** | **Deliberately refused**: a target other than `amd64_win` without `--no-link` errors out immediately, exit 1 |
| **panic handler** | The language **has no panic concept**. `compiler/runtime/no_std_core/panic_handler.jhyy` is an M0 stub (an infinite loop), and it **is not wired into the build** — it is not on the link line |
| **Serial output** | The repository has no UART / COM1 / `0x3f8` code at all. The comment in `std/io.jhyy` says to swap in the syscall implementation "after the OS kernel M11 launch" |
| **`.bss` zeroing / the initial stack** | There is no CRT startup code ⇒ neither of them exists (see section 6) |

These are not "not written yet" — they are boundaries **explicitly on record**. The
deviation table in ABI § 12 is the authoritative list.

---

## 4. The bare metal language surface that is available

| Feature | Status | Limitation |
|---|---|---|
| `#[no_std]` | Available | A module-level attribute; it must define `fn main` |
| `#[link_section("...")]` | Available | It only changes which section a symbol lands in, **it does not change the calling convention**. The section name must be printable ASCII |
| `volatile T` | Available | It only qualifies **primitive types** (qualifying a struct / pointer / array is a compile error); the layout is exactly the same as `T`; every access within a single thread is guaranteed to hit memory and not be reordered. Across threads you need `fence_*` |
| `asm!("...")` | Available but limited | A single string literal; **no operand constraints, no clobber declarations**; AT&T syntax; x86-64 only. The return-value semantics are undefined ⇒ the convention is to write it in statement position |
| `fence_seq_cst()` / `fence_acquire()` / `fence_release()` | Available | They emit `mfence` / `lfence` / `sfence` respectively; only x86-64 is covered |
| `#[naked]` | Available (since v4.1.5) | The label and the function body go through the same channel, and the first instruction is `iret`; the function **must not take parameters** (parameters once made the compiler segfault itself; that is fixed) |
| `defer` | Available | It only covers **explicit `return`** paths; the **implicit return** of the trailing expression in a function body **does not trigger** defer |

Measured artifact (`volatile` + `asm!` + `fence` used together):

```asm
	movl %eax, (%r8)      # volatile store — really writes memory, does not go through the register cache
nop                    # asm!("nop") — inlined at this position
mfence                 # fence_seq_cst() — inlined at the call site
	movl (%r8), %eax      # volatile load
```

Both `asm!` and `fence_*` are **inlined at their position in the function body** (ABI
§ 8). This is not a convenience matter — the early implementation appended them to the
end of the `.s`, where they landed outside all functions as dead bytes, and **the
memory barrier never executed**. That is fixed now.

---

## 5. `#[naked]`: the label and the function body once took two different channels (fixed in v4.1.5)

The `#[naked]` contract: no prologue / epilogue, full control over the registers and
the stack; the function body may contain **only** `asm!(...)` statements (local
variables / control flow / `return` are compile errors).

**v4.1.4 and earlier**: the label went through a side file while the function body
went through the top level of the IL ⇒ the two never met. Measured, the `.s` that
`jhyy build` produced:

```asm
pushq %r15
iret
.text
.balign 16
.globl main_jhyy
main_jhyy:
	...
```

The label `irq_entry:` **does not appear** — the function body lands in **file scope**,
before `.text`. In the linked exe, `<irq_entry>` points at a stretch of alignment
padding (`nop`), not at the function body.

⇒ Back then `#[naked]` compiled, but a **bare interrupt entry point could not be
reached**. The regression case `compiler/tests/examples/naked_interrupt_entry.jhyy`
only asserts a process exit code of 0 — the harness cannot see where a symbol landed,
so no gate caught this.

**From v4.1.5 on**: both ends of naked are merged **onto the same channel** (the
function body goes through the side file too) ⇒ the first instruction is `iret`. The
artifact check `naked_symbol` registered in ledger entry W-223 used to be a KNOWN-FAIL;
this release **removes that line from KNOWN_FAIL** ⇒ it is automatically promoted to a
real gate. It is now one of the artifact checks that have to pass.

The same release also fixed another problem of the same origin: **a `#[naked]`
function with parameters made the compiler segfault itself** (naked's IR is empty, and
codegen emitted the parameter moves as usual, turning those instructions into top-level
instructions and corrupting the IL). Naked functions no longer register parameters and
no longer emit the sret moves — which is also semantically right: naked has no
prologue, so the parameters stay in registers as the ABI prescribes.

---

## 6. The minimal kernel boot path: checked item by item

| Step | Status | Evidence |
|---|---|---|
| Entry symbol | **Supplied by the user**. In the UEFI scenario `efi_main`, in the bare metal / Linux ELF scenario `_start` | Language spec § 17.6 |
| Entry under `#[no_std]` | `main` (the link line has `-Wl,--entry=main`); sema strictly requires `fn main` | ABI § 7 |
| Stack setup | **To be filled in**. There is no CRT startup code ⇒ there is no initial stack. `fn main` itself generates the standard prologue (`pushq %rbp` / `movq %rsp, %rbp` / `subq $N, %rsp`), but the **initial stack** has to be provided by the firmware or by user code | The link line `-nostartfiles` |
| panic handler | **Not implemented**. See section 3 | `no_std_core/panic_handler.jhyy` is not wired into the build |
| Serial output | **Not implemented**. See section 3 | There is no UART code in the repository |
| `.bss` zeroing | **To be filled in**. For the same reason: there is no CRT startup code | — |
| Interrupts / IDT / page tables | **To be filled in**. The language layer has no such facilities | — |

---

## 7. Evidence: the UEFI x64 boot spike

`JiHuiYiYou-OS/spike/boot.s` is a **hand-written GNU assembly** file
(`.intel_syntax noprefix`); it is **not** JHYY code. Its value is that it pins down
the real register convention of the UEFI x64 entry point:

```asm
efi_main:
    # RCX = EFI_HANDLE ImageHandle
    # RDX = EFI_SYSTEM_TABLE *SystemTable
    mov     r12, rdx                   # r12 = ST
    mov     rax, [r12 + 64]            # ConOut (NOT StdErr at 80)
    ...
    call    [r13 + 8]                  # OutputString
```

- **Entry convention**: RCX = ImageHandle, RDX = SystemTable — it matches the MS x64
  convention of `amd64_win_freestanding`.
- **Build line**: `x86_64-w64-mingw32-gcc -nostdlib -Wl,--subsystem,10 -Wl,-e,efi_main -Wl,--image-base=0x10000 -o BOOTX64.EFI boot.s`.
- **Exit code**: `out 0xf4, al` (isa-debug-exit) passes the status to QEMU.
- **Stack**: the spike builds its own frame with `push rbp / mov rbp, rsp`; **nobody
  builds an initial stack for it**.

On the JHYY side: the compiler **does not** generate EFIAPI wrapper code (ABI § 12.8),
so the step from `.s` to `.efi` still has to be written by hand.

---

## 8. Status table of OS / embedded capabilities

| Capability | Status |
|---|---|
| Compiling + linking a `#[no_std]` module | **Available** (measured: the link succeeds, exit code 42) |
| A custom entry symbol (`efi_main` / `_start`) | **Available** — the user writes it, the compiler does not generate it |
| Putting startup code in `#[link_section]` | **Available** (measured: `.section .text.boot` appears in the `.s`) |
| Accessing MMIO with `volatile` | **Available** (measured: it really does go through memory reads and writes) |
| Inline `asm!` | **Available**, limited to a single string literal |
| Memory barriers | **Available** (`mfence` / `lfence` / `sfence` inlined at the call site) |
| A `#[naked]` interrupt entry | **Available** (since v4.1.5: the label and the function body go through the same channel, the first instruction is `iret`) |
| panic / assertions / stack backtraces | **Not implemented** |
| Serial / UART output | **Not implemented** |
| Interrupt controller / IDT / page tables | **Not implemented** |
| Multicore / SMP | **Not implemented** |
| aarch64 / riscv64 bare metal | **Not implemented** (x86-64 only) |
| Automatic UEFI image output | **Not implemented** (the entry path is not finished, ABI § 12.8) |

---

## 9. Related pages

- [CLI reference](/compiler/docs/cli.html) — the four values of `--target=` and the use of `--no-link` for cross targets.
- [ABI v{{abi_version}}](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-abi-v4.0.0.md) — § 7 covers the entry point and linking, § 8 the low-level extensions, § 12 the deviation table.
- [Language spec v{{spec_version}}](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md) — § 17 is `volatile` / `asm!` / `#[naked]` / `#[link_section]` / `#[no_std]` / the memory barriers / the freestanding entry.
- [Targets and cross-compilation](/compiler/download/targets.html) — the artifact shape of the {{targets_count}} targets.
