---
title: Standard Library
description: The real API of the {{stdlib_modules}} modules: arena, mem, string, vec, fmt, io, math, os
layout: docs
project: compiler
zone: docs
---

# Standard Library

JHYY ships with a small standard library of **{{stdlib_modules}} modules**, installed together with the compiler.
Every signature on this page is copied verbatim from the source — `compiler/src0/std/*.jhyy` —
nothing rewritten, and no function filled in that does not exist in the source.

> **The source is the only source of truth**:
> [`compiler/src0/std/`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/tree/main/compiler/src0/std)

---

## How to use it

`import` pulls in a **module**, **without the `std::` prefix** — `import std::vec;` is a parse
error:

```jhyy
import io;
import vec;

fn main_jhyy() -> i32 {
    io::std_io_print("hello from the JHYY stdlib\n");
    0
}
```

Both calling styles have been verified to compile:

| Style | Where it comes from |
|---|---|
| `io::std_io_print(...)` | This is the form the repository README and `compiler/tests/examples/std_io_import.jhyy` use |
| `std_io_print(...)` | The form the spec § 15 prescribes (writing the function name from the source directly) |

⚠ The spec § 15 only acknowledges the second one — it explicitly says "not
`io::std_io_print(...)`"; but the qualified form works in the implementation, and the repository's
own README and regression cases take that route.
Neither of them reports `undefined variable`. **The qualified form is recommended** — names like
`ptr_add` exist in several modules (see the table below), and without qualification it is easy to
point at the wrong one.

The naming style is **historically inconsistent**:

| Style | Modules | Examples |
|---|---|---|
| `<mod>_<fn>` | `mem` / `fmt` / `string` / `arena` | `mem_copy`, `fmt_i32`, `str_concat`, `arena_alloc` |
| `std_<mod>_<fn>` | `io` / `os` / `vec` / `math` | `std_io_print`, `std_os_exit`, `std_vec_new`, `std_math_sin` |

A wrong name is reported as `undefined variable` — there is **no** "did you mean …" hint.
The first time you use a module, copy the names from the table below.

| Module | What problem it solves |
|---|---|
| [`mem`](#mem) | Copying, zeroing, comparing and searching raw memory |
| [`fmt`](#fmt) | Formatting integers / strings into a byte buffer |
| [`string`](#string) | Length-prefixed UTF-8 strings |
| [`vec`](#vec) | Dynamic byte arrays |
| [`arena`](#arena) | bump allocator — request in one go, reuse as a whole |
| [`io`](#io) | File handles and read/write, standard output / error output |
| [`os`](#os) | Raw file descriptors, process exit, environment variables |
| [`math`](#math) | Trigonometry, square root, power (**f64 only**) |

---

## mem

**What problem it solves**: raw memory operations. Everything is a hand-written byte loop — it
**does not call libc**, so the standard library itself does not depend on the libc runtime.

| Signature | What it does |
|---|---|
| `fn ptr_add(p: *u8, off: i64) -> *u8` | Local pointer arithmetic helper |
| `fn mem_copy(dst: *u8, src: *u8, n: i64) -> *u8` | Copies n bytes; returns `dst` |
| `fn mem_compare(a: *u8, b: *u8, n: i64) -> i32` | Compares n bytes: `0` equal / `<0` a<b / `>0` a>b |
| `fn mem_set(dst: *u8, val: i32, n: i64) -> *u8` | Sets n bytes to `val` (low 8 bits); returns `dst` |
| `fn mem_find_byte(p: *u8, n: i64, val: i32) -> i64` | Finds the first byte `== val`; returns the index / `-1` |
| `fn mem_zero(dst: *u8, n: i64) -> *u8` | Zeroes n bytes; returns `dst` |

**Traps**

- ⚠️ **`mem_copy` does not handle overlap** — its semantics match libc `memcpy`.
  For an overlapping region you need `memmove`, which **this module does not implement**.
- Failure semantics: a length `< 0` returns `0` / null (not allowed); a length `0` is a no-op.
- ⚠️ **`mem_set` assumes `dst` is 8-byte aligned.** `arena_alloc` in `std::arena` guarantees
  that, but an **external caller does not** — a `dst` that is not 8-aligned triggers the `#GP` of
  the i64 store.
- `mem_set` writes in i64-store batches plus a u8-store tail (one byte per store; W-075 really fixed).
  Earlier versions used a loop of `*i32`-width stores stepping 1 byte at a time, so **asking for n
  bytes actually wrote 4n bytes**, and the extra part ran over the caller's buffer (W-139 fixed).

---

## fmt

**What problem it solves**: formatting values into bytes. Hand-written; it does not go through the
variadic ABI of libc `printf`.

| Signature | What it does |
|---|---|
| `fn ptr_add(p: *u8, off: i64) -> *u8` | Local pointer arithmetic helper |
| `fn digit_char(d: i32) -> i32` | 0–9 → ASCII code |
| `fn hex_char(d: i32, upper: i32) -> i32` | 0–15 → ASCII code; uses uppercase `A`–`F` when `upper != 0` |
| `fn fmt_i32(out_buf: *u8, val: i32) -> i64` | Writes an i32 in decimal; returns the number of bytes written (excluding `\0`) |
| `fn fmt_i64(out_buf: *u8, val: i64) -> i64` | Writes an i64 in decimal; returns the byte count |
| `fn fmt_str(out_buf: *u8, s: *u8) -> i64` | Copies a cstr into `out_buf`; returns the byte count |
| `fn fmt_hex_u32(out_buf: *u8, val: i32, upper: i32) -> i64` | Writes a u32 in hexadecimal (no `0x` prefix); returns the byte count |

**Traps**

- ⚠️ **`out_buf` must be ≥ 32 bytes.** An i32 needs at most 11 digits + sign + `\0`, an i64 at
  most 20 digits + sign + `\0`, and a hex u32 at most 10 digits + `\0`.
- ⚠️ **There is no float formatting.** `fmt` has no formatting function for `f32` / `f64`.
- ⚠️ **The `val` of `fmt_hex_u32` is the bit pattern of a u32, passed in as an `i32`.**
  When the value is ≥ `0x80000000` it is **negative** — the function converts it by hand into an
  unsigned `i64` before computing.
- `fmt_i32` / `fmt_i64` use division that **truncates toward zero** and do not take the absolute
  value, so `i32::MIN` / `i64::MIN` work out of the box (W-195 really fixed).
  Earlier versions took the absolute value first, and negating `MIN` wrapped back to itself ⇒ only
  a single `-` was printed.

---

## string

**What problem it solves**: length-prefixed UTF-8 strings. A string is represented by a **raw
`*u8` + a length** (the same as the `CapTable` path), and it is **not** a borrow (`&str` is not
done yet).

| Signature | What it does |
|---|---|
| `fn ptr_add(p: *u8, off: i64) -> *u8` | Local pointer arithmetic helper |
| `fn strlen_local(s: *u8) -> i64` | Length of a cstr |
| `fn str_from_cstr(a: *u8, s: *u8) -> *u8` | Copies a cstr into the arena; returns `*StringHeader` |
| `fn str_from_bytes(a: *u8, p: *u8, n: i64) -> *u8` | Copies n bytes; returns `*StringHeader` |
| `fn str_len(s: *u8) -> i64` | Length |
| `fn str_data(s: *u8) -> *u8` | The data pointer (**not guaranteed to be NUL-terminated**) |
| `fn str_concat(a: *u8, x: *u8, y: *u8) -> *u8` | Concatenates x + y into a new arena buffer; returns `*StringHeader` |
| `fn str_equals(x: *u8, y: *u8) -> i32` | `1` equal / `0` |
| `fn str_compare(x: *u8, y: *u8) -> i32` | Lexicographic: `0` equal / `<0` x<y / `>0` x>y |
| `fn str_find(s: *u8, needle: *u8) -> i64` | Finds a substring (the needle must be a cstr); index / `-1` |
| `fn STR_HEADER_SIZE() -> i64` | The byte size of `StringHeader` (16) |

The layout of `StringHeader` is `data: *u8` + `len: i64`, 16 bytes in total.

**Traps**

- ⚠️ **The buffer is not forced to be NUL-terminated** (an M0 simplification). When you need it,
  write `*(data + len) = 0` yourself.
- ⚠️ **Every string buffer is allocated from a mini-arena inside the module** — the caller is
  responsible for `reset` / `free`. This mini-arena is **embedded** in `string.jhyy`; it does not
  reuse the `std::arena` module.
- ⚠️ **The module has 4 more functions of the same name**: `arena_init` / `arena_alloc` /
  `arena_reset` / `arena_free`, all with the signature `*u8` (not `*Arena`).
  They **coexist with the functions of the same name in the `std::arena` module, and do not
  report a redefinition error** — an unqualified call resolves to one of them. To be sure which
  one you are calling, qualify with `string::` / `arena::`.
- The `needle` of `str_find` must be a **cstr** (its length is measured internally with
  `strlen_local`).
- A historical trap: the block layout used to be `[next(8B)][payload...]`, with the start of the
  payload sitting exactly on top of the next pointer's slot
  ⇒ the bytes of the first allocation overwrite the block's next pointer, the linked list is
  corrupted on the spot, and the bump pointer does not advance
  ⇒ allocating two or more strings in a row gives you an ACCESS_VIOLATION (W-141 fixed it to
  `[next(8B)][payload_size(8B)][payload...]`).

---

## vec

**What problem it solves**: dynamic arrays.

⚠️ **One thing first: `Vec` is not a generic container.** Its `elem_size` is a **runtime
parameter**, not a type parameter.

| Signature | What it does |
|---|---|
| `fn std_vec_new(elem_size: i64) -> Vec` | An empty Vec (`data`/`len`/`cap` all 0) |
| `fn std_vec_with_cap(elem_size: i64, cap: i64) -> Vec` | Pre-allocates cap slots; `elem_size ≤ 0` or `cap ≤ 0` returns an empty Vec |
| `fn std_vec_push(v: *Vec, elem_size: i64, src: *u8) -> i32` | Appends 1 element (copies `elem_size` bytes from `src`); returns 1 on success / 0 on OOM |
| `fn std_vec_get(v: *Vec, elem_size: i64, idx: i64) -> *u8` | The element pointer; **returns NULL when out of bounds** |
| `fn std_vec_len(v: *Vec) -> i64` | Number of elements |
| `fn std_vec_cap(v: *Vec) -> i64` | Number of allocated slots (**not bytes**) |
| `fn std_vec_free(v: *Vec) -> i32` | Frees the data buffer and resets |
| `fn std_vec_grow(v: *Vec, elem_size: i64, new_cap: i64) -> i32` | Private helper: doubles cap until ≥ `new_cap` |
| `fn std_vec_byte_copy(dst: *u8, src: *u8, n: i64) -> *u8` | Private helper: copies n bytes |
| `fn VEC_SIZE() -> i64` | The byte size of `Vec` (24) |
| `fn ptr_add(p: *u8, off: i64) -> *u8` | Local pointer arithmetic helper |

The layout of `Vec` is `data: *u8` + `len: i64` + `cap: i64`, 24 bytes in total.

**Traps**

- ⚠️ **`std_vec_get` returns a pointer, not the element value** — because `elem_size` is a
  runtime parameter, the caller dereferences the pointer itself.
- ⚠️ **`std_vec_push` does not check whether `src` is NULL** — it reads `elem_size` bytes from
  `src`. Passing a null pointer in means reading from a null address.
- `std_vec_new` returns a **24-byte struct value** (not a pointer) — the source comments say this
  is to avoid the ABI complexity of sret.
- **It does not rely on full drop semantics** (leak-OK): there is no automatic destructor, and
  `std_vec_free` has to be called by hand.
- The `malloc` failure check in `std_vec_with_cap` was added on 2026-11-07 — before that it would
  return a Vec with `data=NULL`, and the caller would then write into it ⇒ writing to a NULL
  address ⇒ the process crashes outright.

---

## arena

**What problem it solves**: a bump allocator. It requests memory block by block, advances a
pointer linearly inside a block, and can reuse or release a whole block when needed.

> **Read more**: [Arena memory management](/compiler/docs/arena.html) — the allocator model, the
> trade-off against a GC, and when to use it.

| Signature | What it does |
|---|---|
| `fn arena_init(a: *Arena, default_size: i64) -> i32` | Initializes; uses 1 MB when `default_size ≤ 0`. Returns 1 |
| `fn arena_alloc(a: *Arena, size: i64) -> *u8` | 8-byte aligned allocation; returns 0 on failure |
| `fn arena_alloc_aligned(a: *Arena, size: i64, align: i64) -> *u8` | Allocation with a given alignment; returns 0 when `size == 0` |
| `fn arena_calloc(a: *Arena, size: i64) -> *u8` | Allocates and zeroes |
| `fn arena_reset(a: *Arena) -> i32` | Resets the cursor to the start, **without freeing blocks** |
| `fn arena_free(a: *Arena) -> i32` | Frees every block |
| `fn arena_new_block(a: *Arena, size: i64) -> i32` | Private: creates a block and hangs it at the head of the list |
| `fn align_up(x: i64, align: i64) -> i64` | Rounds x up to a multiple of align (align must be a power of 2) |
| `fn ptr_add(p: *u8, off: i64) -> *u8` | Local pointer arithmetic helper |
| `fn ARENA_SIZE() -> i64` | The byte size of `Arena` (40) |
| `fn ARENA_BLOCK_HEADER() -> i64` | The byte size of the block header (16) |

The layout of `Arena` is `start` / `cur` / `end` / `blocks` (all `*u8`) + `def_size: i64`, 40
bytes in total.

**Traps**

- ⚠️ **`arena_reset` used to compute the usable space as `def_size` (1 MB by default),
  while the actual block was not that big — fixed in v4.1.5 (ledger W-222).**
  `arena_init` only records `def_size` and **allocates no block at all**; the real block is
  triggered by `arena_alloc`, and its size is `max(def_size, size + align)`.
  **Before the fix** `arena_reset` set `end` to `start + def_size` ⇒ the arena thought it had
  1 MB available, while under its feet there were only a few dozen bytes ⇒ **later
  allocations wrote straight through the malloc'd block**.

  **The trigger is an allocation size that lands in the `(real block size, def_size]` interval.**
  Measured (2026-11-08, v4.1.4 self-hosted compiler, local machine) — **this is the
  pre-fix behaviour**:

  | Scenario | Result on v4.1.4 and earlier |
  |---|---|
  | `alloc(8)` → `reset` → `alloc(16/32/64)` | Passes (the real 16B block + heap slack is enough) |
  | `alloc(8)` → `reset` → `alloc(128/256/500/1000/1024)` | **ACCESS_VIOLATION (segmentation fault)** |
  | `alloc(8)` → `reset` → `alloc(2000)` | Passes (over `def_size`, so it takes the new-block path) |
  | The same program **without** `reset` | All pass |

  ```jhyy
  import arena;

  fn main_jhyy() -> i32 {
      let mut a: Arena = Arena {
          start: 0 as *u8, cur: 0 as *u8, end: 0 as *u8,
          blocks: 0 as *u8, def_size: 0 as i64,
      };
      arena_init(&a, 1024);
      let p = arena_alloc(&a, 8);
      arena_reset(&a);                    // ← end is set to start + 1024
      let big = arena_alloc(&a, 500);     // ← it thinks there is 1 MB, but only 16 B underfoot
      let mut i: i32 = 0;
      while i < 500 { *(big + i as i64) = 1 as u8; i = i + 1; }   // ← writes straight through
      0
  }
  ```

  Both ends are safe, so this trap is easy to miss: small allocations fit, huge allocations open
  another block, and only the "medium size + after a reset" band blows up.

  **The v4.1.5 fix**: the block header grew from 8 bytes to `next(8) + payload_size(8) = 16`,
  so the **real block size is recorded in the block header**; `arena_reset` now reads it
  back and places `end` there ⇒ no more out-of-bounds writes. Ledger **W-222** (fixed for
  real on 2026-11-09, RESOLVED). After the fix, the standard library copy and the compiler's
  own copy (`compiler/src0/arena.jhyy`) use the **same block-sizing rule**
  (`max(def_size, requested size)`).
- The `blocks` field uses a `*u8` placeholder (JHYY has no self-referential struct), so at the use
  site it has to be cast to `*ArenaBlock`.
- `arena_alloc_aligned` and `arena_new_block` are marked as **private API** in the source
  comments — they are `fn` (so publicly visible), but you are not meant to call them directly.
- The bottom layer uses libc `malloc` (an M0 simplification; the MMAP backend was left to the end
  of v3.x).
- **How to get an `Arena` instance**: a **qualified** struct literal like
  `arena::Arena { ... }` **does not parse**. The workable approach is to declare a local struct
  with the same layout and cast the pointer (`&local as *arena::Arena`), or to `malloc` 40 bytes
  yourself, zero them, and cast.

---

## io

**What problem it solves**: file handles and read/write, plus standard output / error output.
The backend goes through libc's `fopen` / `fread` / `fwrite` / `fclose`.

| Signature | What it does |
|---|---|
| `fn std_io_open(path: *u8, mode: *u8) -> *u8` | Opens a file (`mode` is a cstr: `"r"` / `"w"` / `"wb"` / `"rb"` / `"a"` …); returns `FILE*` / returns 0 on failure |
| `fn std_io_close(f: *u8) -> i32` | Closes; returns `-1` when `f == 0`, otherwise the result of `fclose` |
| `fn std_io_read(f: *u8, buf: *u8, n: i64) -> i64` | Reads n bytes into `buf`; returns the actual byte count (`< n` means EOF / error) |
| `fn std_io_write(f: *u8, buf: *u8, n: i64) -> i64` | Writes n bytes; returns the number of bytes actually written |
| `fn std_io_print(s: *u8) -> i32` | Writes to stdout (cstr); returns `-1` when `s == 0` |
| `fn std_io_print_err(s: *u8) -> i32` | Writes to stderr (cstr); returns `-1` when `s == 0` |
| `fn std_io_eprint(s: *u8) -> i32` | An alias of `std_io_print_err` |

**Traps**

- ⚠️ **`std_io_print` / `std_io_print_err` depend on libc's `stdout` / `stderr` handle access**
  (through the C-side `jh_fputs_stdout` / `jh_fputs_stderr` bridges). That means using them
  **depends on the C runtime** — which conflicts with the `no_std` direction.
- `std_io_read` / `std_io_write` return `-1` when `f == 0`, and `0` when `n <= 0`.
- The source comments say: after the OS kernel M11 launch they have to be swapped for a syscall
  implementation (change the `jh_fputs_*` in `jhyy_helpers.c`), and **not a single line of
  `std/io.jhyy` has to change**.

---

## os

**What problem it solves**: raw file descriptors, process exit, environment variables.

| Signature | What it does |
|---|---|
| `fn std_os_open(path: *u8, flags: i32, mode: i32) -> i64` | `open(2)` wrapper; returns the fd / returns `-1` on failure |
| `fn std_os_close(fd: i64) -> i32` | `close(2)` wrapper; `0` ok / `-1` fail |
| `fn std_os_read(fd: i64, buf: *u8, n: i64) -> i64` | `read(2)` wrapper; returns the byte count, 0 at EOF, `-1` on error |
| `fn std_os_write(fd: i64, buf: *u8, n: i64) -> i64` | `write(2)` wrapper; returns the number of bytes written, `-1` on error |
| `fn std_os_exit(code: i32)` | Terminates the process (**a real exit**, never returns) |
| `fn std_os_getenv(name: *u8) -> *u8` | Reads an environment variable; returns the value as a cstr / returns 0 when not found |
| `fn OS_O_RDONLY() -> i32` | `0` |
| `fn OS_O_WRONLY() -> i32` | `1` |
| `fn OS_O_RDWR() -> i32` | `2` |
| `fn OS_O_CREAT() -> i32` | `64` (`0x40`) |
| `fn OS_O_TRUNC() -> i32` | `512` (`0x200`) |
| `fn OS_O_APPEND() -> i32` | `1024` (`0x400`) |
| `fn OS_MODE_RW_R() -> i32` | `420` (`0644`) |

**Traps**

- ⚠️ **`OS_O_*` / `OS_MODE_RW_R` are zero-argument functions, not constants.**
  The usage is `os::OS_O_CREAT()` — leaving off the parentheses gives you `expected (, got ;`.
- ⚠️ **The `O_*` values are POSIX values** (`O_CREAT = 0x40`), which differ from Windows' `_O_*`
  (`O_CREAT = 0x100`). The platform difference is translated at the C bridge layer; the jhyy side
  keeps POSIX semantics.
- ⚠️ **`std_os_*` go through the 6 libc bridges in `jhyy_helpers.c`**, so they **depend on the C
  runtime again** — the opposite of the "drop the C runtime / zero-C closed loop" direction (W-103
  registered this trade-off).
  For a genuine zero-C setup, what has to be replaced is the **implementation** of the bridges;
  not a single line of `std/os.jhyy` has to change.
- `std_os_open` validates its input: `path == 0`, `flags < 0`, `mode < 0` and `mode > 0777` all
  return `-1` (aligned with the error semantics of libc `open()`).

---

## math

**What problem it solves**: trigonometric functions, square root, power. **f64 only**.

| Signature | What it does |
|---|---|
| `fn std_math_sin(x: f64) -> f64` | `sin(x)`, with x in radians |
| `fn std_math_cos(x: f64) -> f64` | `cos(x)`, with x in radians |
| `fn std_math_sqrt(x: f64) -> f64` | `√x`; `x < 0` → NaN, `x = +∞` → `+∞` |
| `fn std_math_pow(base: f64, exp: f64) -> f64` | `base^exp`, with libm C99 semantics |

**Traps**

- ⚠️ **There is an f64 version only.** No f32, and no `tan` / `log` / `exp` / `floor` / `ceil`.
- It talks to libm directly through FFI (Windows goes through MSVCRT, POSIX through libc + libm) —
  `-lm` is already on the link line.
  It **does not go through the C-side bridge**: the backend's f64 return goes through `%xmm0` +
  `movsd`, so a plain extern is enough.
- The semantics match libm: a finite input returns a finite value, `inf` / `NaN` pass through
  (IEEE 754).
  **No exceptions, no errno**.

---

## Status

The standard library is a **pre-1.0** artifact and **the API will change**. The version comments in
the source read `v3.2.2 (3l.1)` to `v3.2.5 (3l.4)` — that is the module's own iteration numbering,
and it does not represent any compatibility promise.

**This page is maintained by hand.** The ideal state is for the compiler to generate the standard
library documentation itself (extracting the signatures from `compiler/src0/std/*.jhyy`), but that
pipeline does not exist yet — so the signatures may drift from the source. **If they do not match,
the source wins**, and then file an issue.

The related workaround ledger is in
[`docs/internal/workarounds.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/workarounds.md),
and the language-level limitations are in appendix B of the
[language spec v{{spec_version}}](/compiler/docs/spec.html).
