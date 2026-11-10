---
title: ABI v{{abi_version}}
description: Type layout, calling convention and linking rules — the contract by which artifacts recognize each other
layout: docs
project: compiler
zone: docs
---

# ABI v{{abi_version}}

**The original ABI lives in the repository, not here.**
Original: [`docs/abis/jhyy-abi-v4.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-abi-v4.0.0.md)

This page is that ABI's **guided reading**: targets and calling convention, type layout, aggregate
argument passing, linking rules, and a summary of the **known deviations and unimplemented items**.
**Where they conflict, the original in the repository wins.**

The ABI is locked at v{{abi_version}} (2026-10-24, locked together with `v4.0.0 final`), the same generation
as the language spec. The toolchain version is a separate matter, see the
[reference overview](/compiler/docs/reference.html).

---

## Targets and calling convention

| Target triple | Calling convention | Runtime | Status |
|---|---|---|---|
| `amd64_win` (default) | MS x64 | hosted (links the C runtime) | stable |
| `amd64_sysv` | SysV AMD64 | hosted | stable |
| `amd64_win_freestanding` | MS x64 | freestanding | beta |
| `amd64_sysv_freestanding` | SysV AMD64 | freestanding | beta |

- **The architecture is x86-64 only.** aarch64 / riscv64 are not implemented (ABI § 12.10).
- All four targets go through the self-hosted amd64 backend; there is no QBE fallback path.
- The **calling conventions of `amd64_win` and `amd64_win_freestanding` are byte-identical**;
  likewise for `amd64_sysv` and `amd64_sysv_freestanding`.

### MS x64 (`amd64_win` / `amd64_win_freestanding`)

| Rule | Content |
|---|---|
| Integer / pointer arguments | The first 4 go in `RCX` `RDX` `R8` `R9`, the rest go on the stack |
| Floating-point arguments | The first 4 go in `XMM0`–`XMM3`, the rest go on the stack |
| Return value | Integer / pointer → `RAX`; float → `XMM0` |
| Shadow space | The caller reserves 32 bytes on the stack |
| Stack alignment | 16-byte aligned before the `call` |

**Integer and floating-point arguments share the same position counter** — this is the core rule
of MS x64:

| Slot | Integer register | Floating-point register |
|---|---|---|
| 1 | `RCX` | `XMM0` |
| 2 | `RDX` | `XMM1` |
| 3 | `R8` | `XMM2` |
| 4 | `R9` | `XMM3` |
| ≥ 5 | stack | stack |

⇒ In `fn f(a: f64, b: i32)`, `a` is in `XMM0` and `b` is in **`EDX`** (not `ECX`).

### SysV AMD64 (`amd64_sysv` / `amd64_sysv_freestanding`)

| Rule | Content |
|---|---|
| Integer / pointer arguments | The first 6 go in `RDI` `RSI` `RDX` `RCX` `R8` `R9`, the rest go on the stack |
| Floating-point arguments | The first 8 go in `XMM0`–`XMM7`, the rest go on the stack |
| Shadow space | **None** |
| Stack alignment | 16-byte aligned before the `call` |

**Integers and floats are two independent banks** — integers take `rdi`/`rsi`/… in order of
appearance, floats take `xmm0`–`xmm7` in order of appearance, each numbered on its own and
neither affecting the other.
This is **exactly the opposite** of the shared counter in MS x64: the same `fn f(a: f64, b: i32)`
puts `b` in **`RDI`** under SysV.

> When you write a function with mixed int / float arguments, this difference is the easiest thing
> to get wrong — pure JHYY code behaves the same across targets (the return value rules are
> identical), but **hand-written assembly interfacing** will trip on it.

---

## Type layout

| Type | sizeof | alignof | Remarks |
|---|---|---|---|
| `i8` / `u8` | 1 | 1 | Sign / zero extended after loading into 32 bits |
| `i16` / `u16` | 2 | 2 | Same |
| `i32` / `u32` | 4 | 4 | |
| `i64` / `u64` | 8 | 8 | |
| `f32` | 4 | 4 | IEEE 754 binary32 |
| `f64` | 8 | 8 | IEEE 754 binary64 |
| `bool` | 1 | 1 | ⚠️ the compiler **does not normalize to 0/1** |
| `()` | 0 | 1 | Zero-sized type |
| `*T` | 8 | 8 | A null pointer is the integer 0; the step is `sizeof(T)` |
| `fn(...)` function pointer | 8 | 8 | ⚠️ the type position does not accept this syntax (appendix B of the language spec) |
| `[*]T` slice | 16 | 8 | `{ data: *T @0, len: i64 @8 }` |
| `[T; N]` | `N × sizeof(T)` | `alignof(T)` | Elements are contiguous, no padding |
| `&T` / `&mut T` | 8 | 8 | Single pointer; `is_mut` is a compile-time marker |
| `Cap<T>` | 8 | 8 | |
| `PhantomData<T>` | 0 | 1 | ZST, takes no slot in a struct |

- **Signed integer overflow is defined behaviour**: two's-complement wraparound, no runtime check.
- **There is no separate `char` type** — the type of a character literal is `i32`, and the value
  is the Unicode codepoint.
- `struct` is laid out in declaration order with **natural alignment**; nested structs are inlined
  into a single-level layout.
- The tag of an `enum` is `i32` at offset 0; the payload starts at `align_up(4, max_payload_align)`.
- ⚠️ `alignof(enum)` hardcodes **4**, which does not match the natural alignment computed from the
  enum layout (ABI § 12.2).

---

## Aggregate argument passing

### Win

| Argument type | How it is passed |
|---|---|
| `struct` | The caller **builds a copy** on the stack, copying field by field (recursively for nested structs), and passes the address of the copy (one `l` argument) |
| `enum` | **One `l`** (the address of the enum value's own slot), **no copy is built** |
| `[T; N]` | **One `l`** (the address of the array itself), **no copy is built** (effectively by reference) |
| `[*]T` slice | A 16-byte slot `{data, len}`, but **only one `l` pointer** is passed, pointing at that slot |

⚠️ **Only `struct` really builds a copy.** `enum` / `[T; N]` / slices are passed by address — so
modifying the array in the callee modifies the caller's array.

### SysV

| Condition | How it is passed |
|---|---|
| `sizeof ≤ 16` | Classified by eightbyte splitting (INTEGER / SSE), at most 2 eightbytes go into registers |
| `sizeof > 16` | **MEMORY class** — the whole thing lands on the stack |

### Return values

| Return type | Convention |
|---|---|
| Integer / pointer / `&T` | `RAX` |
| `f32` / `f64` | `XMM0` |
| `struct` / `enum` | **Implicit sret**: the caller allocates the return slot and passes it as a **hidden 0th argument** in a register (Win `%rcx` / SysV `%rdi`) |
| `[T; N]` | ⚠️ **Does not use sret**: the callee builds its own 16-byte slot, and `RAX` returns its address |
| `()` | No return value, a bare `ret` at the end of the function |

### Name mangling

| Case | Symbol form |
|---|---|
| Ordinary function | `<name>` |
| Function in a module | `<mod>__<name>` (the call site writes `mod::fn()`) |
| Generic instance | `<Base>$<T1>$<T2>` (e.g. `max$i32`) |
| Generic instance in a module | `<mod>__<Base>$<T1>$<T2>` (the module prefix wins) |
| Closure | `__closure_<N>` (a synthesized name, N increases monotonically on every compilation ⇒ the artifact is reproducible) |
| `extern fn` | **As written**, no prefix, no mangling |

The mangled name of a generic is assembled by the parser in source order, and **contains no pointer
address or hash** ⇒ deterministic.
No overloading is supported.

---

## Program entry and linking

**This section is the easiest thing to get wrong.**

| Mode | Entry symbol | Explanation |
|---|---|---|
| hosted | `main_jhyy` | The C runtime's `main` calls `main_jhyy(argc, argv)`, and its return value becomes the process exit code |
| `#[no_std]` | `main` | Link line `-nostartfiles -nodefaultlibs -Wl,--entry=main -lgcc` |

- `#[no_std]` **does not link the C runtime startup file**; `-lgcc` only provides compiler builtins
  such as `___chkstk_ms`.
- In `#[no_std]` mode `fn main` **must exist**, otherwise it is a compile error:
  `error: #[no_std] module must define 'fn main()'`.

### freestanding does not switch the linking mode

> ⚠️ **The two freestanding targets only switch "calling convention ownership + the entry hook", not the linking mode.**
>
> **The link line branches on whether the source file has `#[no_std]`, and has nothing to do with `--target`.**

| Is there `#[no_std]` in the source file? | Link line |
|---|---|
| **No** | Links `runtime.o` + `helpers.o` (the C runtime bridge) + the Windows system libraries + `-lm` |
| **Yes** | **Does not** link the two above, and instead adds `-nostartfiles -nodefaultlibs -Wl,--entry=main -lgcc` |

In other words: `--target=amd64_win_freestanding` by itself **does not** stop you from linking the
C runtime. To get a purely freestanding artifact, **the source file also has to say `#[no_std]`**.

Both branches carry `-g0 -Wl,--build-id=none -Wl,--stack,67108864 … -lm -lkernel32 -luser32 -lshell32 -ladvapi32`
— **the Windows system libraries and `-lm` are added unconditionally** (also under `#[no_std]`).
A genuine UEFI / bare metal image has to be produced with lld-link
(`/SUBSYSTEM:EFI_APPLICATION /ENTRY:efi_main`) or with a custom link line.

### Target → ABI → linking mode

| Target | ABI (calling convention) | Entry symbol | Linking mode |
|---|---|---|---|
| `amd64_win` | MS x64 | `main_jhyy` | hosted: links the C runtime + the Windows system libraries |
| `amd64_sysv` | SysV AMD64 | `main_jhyy` | hosted (same as above; cross targets require `--no-link`) |
| `amd64_win_freestanding` | MS x64 (byte-identical to `amd64_win`) | User-supplied (`efi_main` / `_start`) | **Depends on whether the source file has `#[no_std]`**, not on `--target` |
| `amd64_sysv_freestanding` | SysV AMD64 (byte-identical to `amd64_sysv`) | User-supplied (`efi_main` / `_start`) | Same |

> ⚠️ **The output container format is not decided by `--target`**, but by the host toolchain's `ld`
> (`link_with_gcc` has no target parameter). The PE / ELF output of the various targets is only
> **convention** (ABI § 12.9).
>
> Corollary: **every target except `amd64_win` can only be built with `--no-link`**, and you take
> the `.s` to a toolchain that matches the target.

---

## FFI

| Direction | Supported argument / return types |
|---|---|
| JHYY → C | All primitive types, `*T`, `bool` |
| C → JHYY | The same |

- `extern fn` only declares, it does not generate a function body; the symbol is resolved by `ld`
  at link time.
- **Not supported**: struct / enum by value across the FFI boundary, variadic functions (the JHYY
  side has to list each argument), callback functions.
- ⚠️ The parameter / return types of `extern fn` are **not restricted at compile time** — declaring
  a struct parameter compiles, but it is actually passed by address, which does not match the C
  ABI (silently mismatched, no error).
- A string literal is a UTF-8 byte sequence stored in the **`.data`** section, NUL-terminated, and
  passed to C as a `*u8`, compatible with C's `char*`.

---

## Known deviations and unimplemented items

ABI § 12 is **deliberately recorded, gated or registered** facts, not omissions.

> The table in § 12 **only lists the items that are still open** — fixed deviations are removed from
> the table and **the numbering shifts accordingly**
> ⇒ when you cite, go by the content of the entry rather than by its number. Summary:

| # | Item | Nature |
|---|---|---|
| 12.1 | **struct / enum return values unconditionally use sret on all targets**, with no size threshold — the SysV standard would put aggregate types of ≤16 bytes into `RAX:RDX` / `XMM0:XMM1` | Deviation from SysV |
| 12.2 | **`alignof(enum)` hardcodes 4**, which does not match the `max(4, max_payload_align)` used to compute the enum layout | Internal inconsistency |
| 12.3 | Non-struct scalar arguments under SysV still borrow the Win classifier to decide the IR letter — currently not wrong, but it is an implicit dependency | Latent risk |
| 12.4 | **Under SysV, mixing MEMORY class arguments with register-spilled arguments → compile-time error**; some legal SysV usages currently do not compile | Capability boundary |
| 12.5 | The sret slot size `max(4, sizeof(T))` and the enum copy written by `total_size` — a theoretical boundary, in practice always identical | Theoretical boundary |
| 12.6 | **Stack slots are only guaranteed to be 8-byte aligned**; there is currently no 16-byte-aligned type, so it is never triggered | Capability boundary |
| 12.7 | **Everything spills, only `RBP` is saved**, so the stack frame is significantly larger, compensated by the 64 MB stack reservation | Implementation characteristic |
| **12.8** | **The UEFI EFIAPI wrapper is not implemented**: the two freestanding hooks (`emit_entry_point` / `no_crt_init`) are **both empty implementations** — the compiler emits no EFIAPI wrapper and does not automatically suppress the CRT / runtime linking. The entry symbol is supplied by the user | **Not implemented** |
| 12.9 | **No cross-compilation container backend**: `--target` does not switch between PE / ELF output | Capability boundary |
| 12.10 | **No aarch64 / riscv64**; the `.jhyynb` native binary format is still a design draft, not implemented | Not implemented |
| 12.11 | The SysV eightbyte width rule **only holds for the 0th eightbyte** — the 1st and later ones are always 8 bytes | Deviation from SysV |
| 12.12 | Spilled `f64` stack arguments under SysV lack 16-byte alignment | Deviation from SysV |
| 12.14 | **The Windows console UTF-8 is set by the runtime**: the `main` in `runtime.c` calls `SetConsoleOutputCP(CP_UTF8)` + `SetConsoleCP(CP_UTF8)` **when stdout is a console**; with a pipe / redirection the code page is left alone | Implementation characteristic |

> § 12.14 is the only item in this group that the **user can see directly**: the default OEM code
> page on Chinese Windows is CP936 / GBK, so the UTF-8 bytes a program `printf`s out get
> interpreted as GBK ⇒ the screen is full of mojibake.
> The runtime only switches the code page when stdout is a console, precisely to avoid this trap.

> **§ 12.8 is currently the biggest gap**: the freestanding targets are marked beta not because the
> convention is undefined, but because **the entry path is not wired up yet**. The user has to
> supply `efi_main` or `_start` themselves.

---

## Stability promise

ABI § 9 explicitly splits into two columns:

| **Locked** in this version (does not change with minor / patch) | **May** change in later versions |
|---|---|
| The sizeof / alignof of the primitive types | The sret handling of struct / enum return values on SysV |
| The pointer width (64-bit) | The value of `alignof(enum)` |
| The struct field alignment and ordering algorithm | The name mangling scheme (introducing type encoding / overload encoding) |
| The layout of the enum tag (`i32`, offset 0) | How the SysV classifier handles non-struct scalars |
| The calling convention ownership of the four targets (which target uses which convention) | The granularity of stack slot alignment |
| The basic shape of the name mangling scheme (`<mod>__<name>` / `<Base>$<T>`) | |

---

## The original

- ABI v{{abi_version}} (locked) —
  [`docs/abis/jhyy-abi-v4.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-abi-v4.0.0.md)
- Companion language spec v{{spec_version}} (locked) —
  [`docs/abis/jhyy-lang-spec-v4.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md)
- Known limitation ledger —
  [`docs/internal/workarounds.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/workarounds.md)
- Binary format (design draft, not implemented) —
  [`docs/abis/jhyy-binary-format-v1.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-binary-format-v1.0.0.md)
