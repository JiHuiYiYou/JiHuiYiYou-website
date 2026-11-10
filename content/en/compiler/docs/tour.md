---
title: Language Tour
description: A quick look at the shape of the language: types, procedures, modules, FFI
layout: docs
project: compiler
zone: docs
---

# Language Tour

This is a tour, not the spec. The **language spec** is the authority — it is locked, and the known
limitations are collected in its appendix B:
[spec](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md).

---

## The overall shape of the language

**Statically typed. Expression-oriented. Compiled to native code.**

```jhyy
type Point = struct { x: i32, y: i32 }

fn dist_sq(a: Point, b: Point) -> i32 {
    let dx = a.x - b.x;
    let dy = a.y - b.y;
    dx * dx + dy * dy
}

fn classify(n: i32) -> *u8 {
    match n {
        0        => "zero",
        1..10    => "single digit",
        10 | 20  => "round number",
        _        => "other",
    }
}

extern fn printf(fmt: *u8, val: i32) -> i32;

fn main_jhyy() -> i32 {
    let p = Point { x: 3, y: 4 };
    let q = Point { x: 0, y: 0 };
    printf("d² = %d\n", dist_sq(p, q));
    printf("%s\n", classify(42));
    0
}
```

Three things are worth noting:

- A function body is an **expression** — the last expression is the return value.
- `if`, `match` and blocks are values themselves, not just statements.
- A string literal **is** a `*u8` (NUL-terminated UTF-8 bytes in the `.data` section); no conversion
  is needed.

---

## What is supported

| Category | Supported |
|---|---|
| **Types** | `i8/i16/i32/i64`, `u8/u16/u32/u64`, `f32/f64`, `bool`, `*T`, `[T; N]`, `[*]T` (slices), `struct`, `enum`, `Cap<T>`, `PhantomData<T>` |
| **Size** | `sizeof(T)` / `alignof(T)` — compile-time constants |
| **Conversion** | `as` — integer/float conversion, widening/narrowing, `*T ↔ i64/u64` |
| **Control flow** | `if`/`else` (with a value), `while`, `for i in start..end`, `break`, `continue`, `match` (literal/range/enum/wildcard, with exhaustiveness checking) |
| **Cleanup** | `defer` — runs LIFO on scope exit; does not run on an implicit tail return |
| **Top-level constants** | `const NAME: [T; N] = [...]` — emitted into the `.data` section at compile time |
| **Logic** | `&&` / `\|\|` short-circuit, `!` / `~` unary |
| **Functions** | first-class functions, recursion, compound assignment (`+=` `-=` `*=` `/=` `%=`), block-expression closures (they cannot capture — capturing is a compile error) |
| **Modules** | `import` + transitive imports, multi-file CLI, `mod::fn()` namespace |
| **FFI** | `extern fn` calling into C (printf, file I/O, multiple arguments) |
| **OS / embedded** | `#[no_std]`, `#[naked]`, `#[link_section]`, `volatile`, inline `asm!`, memory barriers |
| **Standard library** | `import mem;` / `fmt` / `io` / `math` / `string` / `vec` / `os` / `arena` — **note: no `std::` prefix** |

### Four capabilities that are most often misread

| Capability | Status | What it actually means |
|---|---|---|
| `[*]T` (slice) | Available | It is a **view** over an array — writes go back to the original array, and indexing **is not bounds-checked** |
| `PhantomData<T>` | Type level only | Legal as a struct field; but instantiating it is a compile error |
| `asm!` | Restricted | **It must be a string literal** — no operand constraints, no clobbers; AT&T syntax, x86-64 only |
| `Cap<T>` | Layout only | The 8-byte layout is fixed and testable, but you cannot construct a value yet — real capability semantics are on the roadmap |

---

## Modules and the standard library

`import` pulls in a module. **There is no `std::` prefix** — `import std::vec;` is a compile error.

```jhyy
import io;

extern fn puts(s: *u8) -> i32;

fn main_jhyy() -> i32 {
    io::std_io_print("hello from the JHYY stdlib\n");
    puts("and from libc, through extern fn");
    0
}
```

| Module | What it provides |
|---|---|
| `mem` | `mem_copy` / `mem_set` / `mem_zero` / `mem_compare` / `mem_find_byte` |
| `fmt` | `fmt_i32` / `fmt_i64` / `fmt_str` / `fmt_hex_u32` — format into a byte buffer |
| `io` | file I/O (`std_io_open` / `std_io_read` / `std_io_write` / `std_io_close`) + `std_io_print` / `std_io_print_err` |
| `math` | `std_math_sin` / `std_math_cos` / `std_math_sqrt` / `std_math_pow` |
| `string` | length-prefixed strings: `str_from_cstr` / `str_concat` / `str_find` / `str_len` |
| `vec` | `std_vec_new` / `std_vec_push` / `std_vec_get` — a byte vector, **generic elements are not possible yet** |
| `os` | raw POSIX / Win32 file descriptors + `std_os_getenv` |
| `arena` | bump allocator: `arena_init` / `arena_alloc` / `arena_reset` |

---

## Talking to C

```jhyy
extern fn printf(fmt: *u8, val: i32) -> i32;
```

`extern fn` calls C functions under the C ABI. Two things to remember:

- **There is no variadic form.** Every C argument has to be written out one by one.
- **Argument types are not checked against the C signature.** Write it wrong and it still compiles;
  the problem only shows up at runtime.

For struct layout and calling convention see the
[ABI whitepaper](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-abi-v4.0.0.md).

---

## Memory

**There is no garbage collection and no RAII.** Memory is yours to manage:

- explicit pointers (`*T`), and manual allocation through the runtime's arena or your own allocator;
- if you want, `defer` for scope-exit cleanup — it runs LIFO (but not on an implicit tail return);
- the standard library has `arena`; use it directly where it fits.

This is a deliberate choice: the language targets systems work, where a predictable memory model
matters more than convenience.

---

## What is **not** there yet

Listed honestly — the project is pre-1.0 and says so itself:

| You want to… | Today |
|---|---|
| Use generics with traits | Not yet — queued behind the OS line |
| Use closures that capture variables | Not yet — capturing is a compile error today |
| Print floating-point numbers | Not yet — `fmt` has no float formatting |
| Target aarch64 / riscv64 | Not yet — x86-64 only |
| Put it into production | Not yet — the spec is still moving |

The authoritative list (with versions) is in the repository's
[FACTS.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md);
the item-by-item limitations are in appendix B of the spec.

---

## What's next

- [[Build-and-Test]] — write something and verify it.
- [[FAQ]] — frequently asked questions about the language.
- [[Architecture]] — where the source goes after the parser.
