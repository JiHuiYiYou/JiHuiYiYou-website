---
title: Arena memory management
description: The mental model behind arena, the real API, its lifetime, and common misuse
layout: docs
project: compiler
zone: docs
---

JHYY's `arena` is a **bump allocator**: allocating pushes the cursor forward, and
freeing does nothing. But it is **not** the kind of arena that has "only alloc, no
free" — the same API offers both a reset (`arena_reset`, which reuses the memory) and
a whole-block free (`arena_free`). This page lays out its real signatures, its memory
layout, its lifetime, and a few places that bite.

First, the most important thing: **JHYY has two arenas, and the one the compiler uses
internally is not the same thing as the one you get from `import arena;`.** Their APIs
are equivalent, their implementations are separate, and neither imports the other.
Section 3 explains how to tell them apart.

---

## 1. Mental model

One allocation does three things:

1. See whether the current block has enough room left;
2. If not, open a new block (libc `malloc` underneath);
3. Push the cursor `cur` forward and return the aligned pointer.

| Operation | What happens to the memory |
|---|---|
| `arena_alloc` / `arena_calloc` | The cursor advances; a new block is opened when there is not enough room |
| `arena_reset` | The cursor **rewinds**; **no** block is freed, the memory is kept for reuse |
| `arena_free` | It walks the list and **frees each block** with `free`; afterwards the arena's pointer fields are zeroed |

No GC, no destructors, no reference counting. **Whoever allocates is responsible for
deciding when it becomes invalid.**

---

## 2. The real API

The source of truth is `compiler/src0/std/arena.jhyy`; the signatures are copied
verbatim:

```jhyy
type Arena = struct {
    start:    *u8,
    cur:      *u8,
    end:      *u8,
    blocks:   *u8,         // *ArenaBlock head (使用处 cast)
    def_size: i64,
}
```

| Function | Signature | Returns |
|---|---|---|
| `arena_init` | `fn arena_init(a: *Arena, default_size: i64) -> i32` | always `1` |
| `arena_alloc` | `fn arena_alloc(a: *Arena, size: i64) -> *u8` | an 8-byte-aligned pointer; **returns `0` on failure** |
| `arena_calloc` | `fn arena_calloc(a: *Arena, size: i64) -> *u8` | the same, and **zeroes the whole block** |
| `arena_reset` | `fn arena_reset(a: *Arena) -> i32` | always `1` |
| `arena_free` | `fn arena_free(a: *Arena) -> i32` | always `1` |

The same module also has `arena_alloc_aligned(a, size, align)`, `arena_new_block`,
`align_up`, `ptr_add` (the module table in the language spec § 15 lists them under
`arena` as well).

A few details you have to know:

- **Alignment**: internally, `arena_alloc` is `arena_alloc_aligned(a, size, 8)` ⇒
  guarantees **8-byte alignment**.
- **Failure**: when `malloc` fails, `arena_alloc` returns the null pointer `0`. **No
  panic, no error thrown** — the caller has to check it itself.
- **`size == 0`**: `arena_alloc(a, 0)` returns `0` directly, so `arena_calloc(a, 0)`
  returns `0` too — that is not a valid zero-length block of memory.
- **`arena_init`'s `default_size`**: when `<= 0`, **1 MB (1048576 bytes)** is recorded
  in `def_size`.
- **The return codes carry almost no information**: `init` / `reset` / `free` always
  return `1`. The only thing worth checking is the null pointer from `alloc` /
  `calloc`.

The byte layout of `Arena` (as written in the source comment): `start`(8), `cur`(8),
`end`(8), `blocks`(8) and `def_size`(8) add up to **40 bytes**. `blocks` is the head of the
linked list — JHYY does not support self-referential structs, so in the source it is a
placeholder of type `*u8` and is cast at the use site.

---

## 3. Two arenas side by side

| | The compiler-internal one | The user-side standard library one |
|---|---|---|
| File | `compiler/src0/arena.jhyy` | `compiler/src0/std/arena.jhyy` |
| Who uses it | The compiler itself (AST / IL / codegen nodes all live in it) | Your program: `import arena;` |
| Block header size | 16 bytes | 8 bytes |
| Block size | `max(def_size, this request + alignment padding)` | `this request + alignment padding` (**`def_size` is ignored entirely**) |
| Extra functions | One extra `arena_strdup` | None |

**Why they are separate** (the source comment says): the internal jhyy-side
implementation does not import `src0/arena.jhyy`, **to avoid mangle complexity**; two
arenas exist side by side — the compiler uses `src0/arena.jhyy`, the standard library
user uses `std::Arena`.

**How to tell them apart**: the lookup order for `import arena;` is **next to the main
file → the standard library directory** (a two-level fallback).

- During the self-hosted build the main file is `compiler/src0/main.jhyy`, and there
  is an `arena.jhyy` next to it ⇒ the compiler gets the internal one.
- There is no `arena.jhyy` next to your program ⇒ it falls through to the standard
  library directory ⇒ you get the `std/arena.jhyy` one.

You do not have to distinguish this in your code, but **you have to know that what you
got is not the compiler's internal one** — the two have different block-sizing
strategies, and that directly affects the behavior of `arena_reset` (see 5.1).

---

## 4. Growth strategy: the M0 simplification

The source comment says:

> The backend's alloc goes through libc malloc (an M0 simplification; the MMAP backend
> is left for the end of v3.x)

In other words: **the underlying allocator is libc `malloc`**. No mmap, no page
allocation, no huge pages. The MMAP backend is something planned for a later version;
it does not exist now.

This leads to a counterintuitive measured result: `arena_init(&a, 65536)` **does not
preallocate 64 KB**. Measured, the data area of the first block is only **16 bytes**
(= an 8-byte request + 8 bytes of alignment padding).

In the standard library implementation, `def_size` **is only used by `arena_reset`** —
the allocation path never looks at it.

---

## 5. A complete lifetime

```jhyy
import arena;

fn main_jhyy() -> i32 {
    // 1. init: only records def_size, does not preallocate memory
    let mut a: Arena = Arena { start: 0 as *u8, cur: 0 as *u8, end: 0 as *u8,
                               blocks: 0 as *u8, def_size: 0 as i64 };
    arena_init(&a, 65536 as i64);

    // 2. alloc: 8-byte aligned; returns 0 on failure, you have to check it
    let p = arena_alloc(&a, 8 as i64);
    if p == (0 as *u8) { return 1 as i32; }
    *(p as *i32) = 42 as i32;

    // 3. calloc: allocate + zero the whole block
    let z = arena_calloc(&a, 16 as i64);
    if z == (0 as *u8) { return 2 as i32; }

    // 4. use: the data stays valid until reset / free
    let v = *(p as *i32);

    // 5. free: releases every block; after that any old pointer is dangling
    arena_free(&a);
    return v;
}
```

The functions in the module can also be called with a qualified name:
`arena::arena_init(&a, 65536)`, `arena::arena_alloc(&a, 8)` — the two forms are
equivalent.

### 5.1 Two counterintuitive things about reset

**One: reset returns to the start of "the most recent block", not to the start of the
arena.** In the source, `blocks` is a stack-like list (new blocks are pushed onto the
head), and `arena_reset` takes the block at the head. Measured: `alloc(8)` first, then
`alloc(4096)` (which triggers a new block); after `reset`, a further `alloc(8)` gets
the address of **the 4096 block**, not the first one. The earlier blocks are still
hanging on the list (they are only freed together by `arena_free`), but after a reset
they are never allocated from again.

**Two: the usable window after a reset used to be computed from `def_size` — fixed in
v4.1.5.** `arena_reset` used to set `end` to `start + def_size`, while the actual
block size is "request + alignment padding". When `def_size` is larger, the arena
"thinks" it has a big block available.

The measured consequence (`arena_init(&a, 65536)` → `alloc(8)` → `reset` →
`alloc(4096)` → write all 4096 bytes): the pointer returned by `alloc(4096)` lands
**outside** the actual block; on process exit Windows reports **HEAP_CORRUPTION**
(`0xC0000374`).

**The triggering interval is deterministic**: an allocation size that falls between
`(the real block size, def_size]` overflows, while both ends are safe — so this trap
is easy to miss.

| Scenario (`arena_init(&a, 1024)` → `alloc(8)` → `reset` → allocate N and write all N bytes) | Result on v4.1.4 and earlier |
|---|---|
| N = 16 / 32 / 64 | passes (the real block is 16 B and the heap slack is enough) |
| N = 128 / 256 / 500 / 1000 / 1024 | **out of bounds — segmentation fault / HEAP_CORRUPTION** |
| N = 2000 | passes (it exceeds `def_size`, so it takes the new-block path) |
| The same program **without** `reset` | all pass |

**The v4.1.5 fix**: the block size becomes `max(def_size, the requested size)` and is
**recorded in the block header** (`payload_size`) ⇒ `arena_reset` reads the real size
back from the block header and no longer overflows. Ledger entry W-222.

The same release also added **test coverage** for this: `std::arena` previously had
**zero test coverage** — `compiler/tests/examples/arena_reset.jhyy` is an inline copy,
and it has a simpler implementation (it only resets `cur` and does not touch `end`) ⇒
the real thing was never tested. There is now
`compiler/tests/examples/std_arena_reset/std_arena_reset.jhyy`, and it **must** stay
in a directory with "no local `arena.jhyy`", otherwise `import arena;` will hit that
copy.

### 5.2 Safe usage

- `arena_reset` is only safe when **every subsequent allocation is no larger than the
  actual size of the block before the reset**.
- If you want "start the whole round over", the least-effort approach is
  **`arena_free` + `arena_init`**, which does not depend on the window semantics of
  reset.
- After `arena_free` all four pointer fields of the arena are zeroed (`def_size` is
  kept). **Using an old pointer after free = a dangling pointer** — JHYY has neither a
  GC nor automatic destructors to save you.

### 5.3 When to reset, when to free

| Scenario | Use |
|---|---|
| One-off temporary data (parsing, compiler intermediate state) | `arena_free` |
| Reusing the same memory each round (mind the window constraint in 5.1) | `arena_reset` |
| Process exit | `arena_free` |
| Data that has to survive across phases | **do not put it in an arena** — use `malloc` or `Vec` |

### 5.4 Choosing between arena, Vec, and malloc

The standard library offers two other options: `import vec;` (`Vec<T>`, 24 bytes
`{data, len, cap}`, with `std_vec_new` / `std_vec_push` / `std_vec_get` /
`std_vec_free`) and `extern fn malloc` / `free`.

| | arena | `Vec<T>` | `malloc` / `free` |
|---|---|---|---|
| Allocation unit | whole-block bump advance | element by element via push, growing automatically | one at a time |
| Release granularity | the whole block (`arena_free`) or reuse (`arena_reset`) | the whole Vec (`std_vec_free`) | each allocation is yours to manage |
| Bounds checking | none | `std_vec_get` returns a null pointer when out of bounds | none |
| Good for | one-off, batched temporary objects | sequences whose length changes | single objects, buffers handed to C |

JHYY has no GC, no destructors, and no `drop`. **Picking the wrong one does not raise
an error — it just reads garbage at some point or crashes.**

---

## 6. Relationship to inline assembly / DMA / MMIO

The source and the ABI have **no** dedicated convention relating arena to these three.
What follows is an **inference** from the fact that "the arena's underlying allocator
is libc `malloc`"; it is marked as such so you know where the boundary lies.

| Scenario | Conclusion |
|---|---|
| Using an arena pointer in inline assembly | Allowed. The pointer is an ordinary memory address with 8-byte alignment. But `asm!` accepts only a single string literal, with no operand constraints and no clobber declarations ⇒ you can only pass it through a `volatile` variable or a fixed address |
| MMIO registers | **Not allowed.** What the arena gives you is ordinary memory in the process's virtual address space, whereas MMIO needs a device address. Use a `volatile i32` with a fixed address (a symbol declared `extern`) |
| DMA buffers | **Not allowed** (currently). DMA needs a device-visible physical address / pinned memory; the arena gives you ordinary pageable heap memory that the kernel may move. Doing DMA means writing your own allocator |

---

## 7. Anti-patterns

| Anti-pattern | Consequence |
|---|---|
| **Cross-arena reference**: a struct in arena A holds a pointer into arena B | After `arena_free(B)` the pointer in A dangles. There is no shared lifetime convention between the two arenas |
| **Use after the arena is destroyed** | A dangling pointer. JHYY does not report it; it crashes at runtime |
| **Allocating long-lived data in an arena that is about to be reset** | After the reset that data is all overwritten — the arena has **no** marking of "which data is long-lived" |
| **Using an arena handle inside a closure** | **The compiler rejects it outright**: JHYY closures do not support capture; capturing is a compile error. The variant that does compile is to store a `*Arena` in a struct or a global and use it elsewhere — that is still an escape |

---

## 8. Related pages

- [Standard library](/compiler/docs/stdlib.html) — the API summary of the eight modules.
- [Language spec v4.0.0](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md) — § 15 is the module API table, Appendix B lists the unimplemented items.
- [ABI v4.0.0](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-abi-v4.0.0.md) — § 4.3 explains that "the compiler itself does not implement a heap".
