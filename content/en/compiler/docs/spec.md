---
title: Language Spec v{{spec_version}}
description: The locked language contract: syntax, type system, semantic boundaries
layout: docs
project: compiler
zone: docs
---

# Language Spec v{{spec_version}}

**The full spec lives in the repository, not here.**
Original: [`docs/abis/jhyy-lang-spec-v4.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md)

This page is that spec's **guided reading + index + summary of the key conventions**. Every item in
the body of the spec corresponds to reproducible behaviour in the compiler source; every item on
this page does too. **Where the two conflict, the original in the repository wins.**

The spec is locked at v{{spec_version}} (2026-10-24, locked together with `v4.0.0 final`). The toolchain
version is a separate matter, see the [reference overview](/compiler/docs/reference.html).

---

## What the spec covers

| Chapter | Contents |
|---|---|
| § 1 | Program structure: the `main_jhyy` entry point, `import` across multiple files, comments, top-level declarations |
| § 2 | Type system: primitive types, compound types, aliases, inference, literals, `Cap<T>`, `PhantomData<T>`, `sizeof`/`alignof` |
| § 3 | Variables and bindings: `let` / `let mut`, shadowing, top-level global variables, compound assignment |
| § 4 | Operators: 12 precedence levels, semantic essentials, equality comparison for aggregate types, `as` conversion |
| § 5 | Control flow: `if`/`else`, `while`, `for`, `break`/`continue`, `return`, `match`, closures |
| § 6 | Functions: signatures, recursion, `defer`, attributes |
| § 7 | Pointers and borrows: `&x`, pointer arithmetic, `&T` / `&mut T` |
| § 8–9 | `struct`, `enum` |
| § 10 | Fixed-length arrays and slices |
| § 11 | Generics: struct / enum / functions, turbofish, inference at the call site |
| § 12 | Top-level `const` arrays |
| § 13 | Modules and imports |
| § 14 | FFI (`extern fn`) |
| § 15 | Standard library ({{stdlib_modules}} modules) |
| § 16 | Command line |
| § 17 | Low-level and OS extensions: `volatile`, `asm!`, `#[naked]`, `#[link_section]`, `#[no_std]`, memory barriers, freestanding |
| § 18 | Error codes and diagnostics |
| § 19–20 | Debug ABI and wire format (cross-project contracts) |
| Appendices A–D | Differences from v1.3.0, the list of what is not implemented, self-hosting compatibility, complete examples |

---

## Key conventions

The table below is **the batch you are most likely to get wrong while writing code**. The full
statements are in the corresponding chapters of the original spec.

### Type system

| Convention | Content |
|---|---|
| Primitive types | `i8 i16 i32 i64 u8 u16 u32 u64 f32 f64 bool`, plus the zero-sized type `()` |
| No `char` | The type of a character literal is `i32`, and the value is the Unicode codepoint (the full range U+0000–U+10FFFF) |
| `()` | Is a ZST (sizeof 0 / alignof 1), but **the type position does not accept it**: `let x: () = ();` is a parse error |
| Compound types | `*T` / `[T; N]` / `[*]T` / `struct` / `enum` / `&T` / `&mut T` / `Cap<T>` / `PhantomData<T>` / `volatile T` |
| `fn(...)` type | **The type position does not accept this syntax** ⇒ a closure value cannot be passed as a function value |
| Nominal types | `struct` / `enum` are compared **by declaration name**, not by layout — the same layout with a different name is a different type |
| Type aliases | Transparent: `type Age = i32` is exactly equivalent to `i32` |
| Inference | Parameters **must** be annotated explicitly; local variables are inferred from the initializer expression |
| Default literal types | Unsuffixed integer → `i32`; unsuffixed float → `f64` |
| Implicit conversions | Integer ↔ float **not allowed**, `as` is required |

### Literals

| Convention | Content |
|---|---|
| Integer bases | Decimal / `0x` / `0X` / `0o` / `0O` / `0b` / `0B`; **a leading zero means octal** (`077` = 63) |
| Underscore separators | `1_000_000` is **not supported** (parse error) |
| Integer suffixes | `i8 i16 i32 i64 u8 u16 u32 u64` |
| Integer value range | Evaluated exactly as `u64`; out of range is a **compile error** (`integer literal out of range`), **no silent saturation** |
| Float forms | Only `N.M` (suffixes allowed) — **the exponent form `1.0e10` fails to parse** |
| Float suffixes | `f32` / `f64` / `f` (`f` = `f64`) |
| Strings | The type is `*u8` (a NUL-terminated UTF-8 byte string), placed in the **`.data` section**; **no implicit decay** to `[*]u8` |
| Booleans | `true` / `false`; the compiler **does not normalize to 0/1** — a `bool` that does not come from a literal may be any byte |

### Functions and procedures

| Convention | Content |
|---|---|
| Return value | The **last expression** of the function body is the return value, no `return` needed |
| Parameters | Must be annotated explicitly; **default parameters and variadic parameters are not supported** |
| Nesting | **Nested functions are not supported** — every function must be declared at the top level |
| `defer` | Runs LIFO on the **explicit `return`** path; ⚠️ **the implicit return of the trailing expression does not trigger defer** |
| `#[inline]` | Actually inlined only when the **function body is a single `return <expr>;`**; multiple statements / if-else / loops / recursion all fall back to a plain `call` |

### Modules and imports

| Convention | Content |
|---|---|
| Syntax | A single identifier: `import mylib;` — **without the `std::` prefix** (`import std::vec;` is a parse error) |
| Lookup order | Next to the main file → the standard library directory (two-level fallback) |
| Transitivity | Recursive: with `main → a → b`, `main` can use the declarations of `b` |
| Cycles | A cycle reports `circular import '...'`, it does not crash |
| Namespaces | Different modules may define functions with the same name; qualify the call with `mod::fn()` |
| Multiple files | Composition is done with `import`, **not on the command line** — the command line accepts only one input file, and extra `.jhyy` arguments are **silently ignored** |

### enum and match

| Convention | Content |
|---|---|
| enum layout | The tag is `i32`, offset 0, increasing from 0 in declaration order |
| Payload | **At most one payload per variant** (`Rect(i32, i32)` is a parse error) — to hold several fields, replace the payload with a struct |
| match patterns | Literal / `_` / multi-value `pat1 \| pat2` / range / enum binding |
| Range semantics | ⚠️ **`0..10` in a match is a closed interval (both ends included)**, while `for i in 0..10` is a half-open interval |
| arm body | Must be a **single expression** — you cannot write `return`, and you cannot write a statement block |
| arm scope | Each arm is independent, pattern bindings **shadow** outer variables of the same name, and they do not leak out after the arm ends |
| Exhaustiveness | Implemented: every variant of an enum must be covered or caught by `_`, otherwise `non-exhaustive match: missing variant` is reported |
| Not supported | **Guard patterns** (`Some(x) if x > 0`); **nested patterns beyond the second level** (rejected at compile time) |

### Pointers and borrows

| Convention | Content |
|---|---|
| Pointer width | 8 bytes; a null pointer is the integer 0; the arithmetic step is `sizeof(T)` |
| `&x` | The type is `*i32`; ⚠️ the compiler **does not check** whether `x` is mutable — an immutable binding can have its address taken |
| Pointer difference | The result of `p - q` is the **number of elements** (`i64`), not the difference in bytes |
| Member access | ⚠️ **`->` is not the member access operator** — to reach a field through a pointer write `(*p).field` |
| `&T` / `&mut T` | Both are 8-byte single pointers; `is_mut` is a compile-time marker and takes no memory |
| Not supported | Chained `&&T`; lifetime annotations `'a`; reborrow |
| Borrow checking | Only a minimum is done — repeated `&mut` of the same variable in one scope is rejected; full NLL / Polonius is **not implemented** |

### FFI (`extern fn`)

| Convention | Content |
|---|---|
| Semantics | Declaration only, no function body is generated; the symbol is resolved by `ld` at link time |
| Symbols | Assembly symbols are **unmangled** |
| Variadic | **Not supported** — every argument of `printf` must be listed one by one on the JHYY side |
| Callbacks | **Not supported** |
| struct / enum by value | **Not supported** across the FFI boundary |
| ⚠️ No type checking | The parameter / return types of `extern fn` are **not restricted at compile time** — declaring a struct parameter compiles, but it is actually passed by address, which does not match the C ABI (silently mismatched, no error) |

### Attributes

| Attribute | What it does |
|---|---|
| `#[inline]` | Hints at inlining (see above) |
| `#[naked]` | No prologue / epilogue; the function body may **only** contain `asm!(...)`; it does not take part in sret; the callee has to save the callee-saved registers itself |
| `#[link_section("...")]` | Only changes the section the symbol lands in, it **does not change the calling convention**; the section name must be printable ASCII |
| `#[no_std]` | A **module-level** attribute; does not link the C runtime startup file, and the entry symbol becomes `main`; without `fn main` it reports `error: #[no_std] module must define 'fn main()'` |

### Inline assembly and memory barriers

| Convention | Content |
|---|---|
| `asm!("...")` | A single string literal; **no operand constraints, no template placeholders, no clobber declarations**; AT&T syntax, x86-64 only |
| Placement | **Inlined at the current position in the function body** (hex-encoded into the `dbgasm` channel of the IL, and the backend decodes it back in place into the `.s`) — the early implementation appended it to the end of the `.s`, which made it dead bytes |
| Expression position | Syntactically usable, but **the return value semantics are undefined** ⇒ by convention it is written in statement position |
| `volatile T` | Qualifies **primitive types only**; the layout is exactly the same as `T`; within a single thread it guarantees that every load hits memory, that every store writes back, and that they are not reordered |
| `fence_*` | `fence_seq_cst()` / `fence_acquire()` / `fence_release()` → `mfence` / `lfence` / `sfence`; inlined at the call site; **covers x86-64 only** |
| Across threads | `volatile` **does not provide** ordering guarantees across threads — that is what `fence_*` is for |

### Other easy traps

| Convention | Content |
|---|---|
| Top-level `let mut` | It is a **runtime global variable**, but the initializer **must be an integer constant expression**; an initializer of a non-integer type is discarded (you read 0 or garbage) |
| Top-level `const` | Only **top-level** `const` arrays are supported; putting a function call in an element position compiles, but it is not evaluated (you get 0 at runtime) |
| `sizeof` / `alignof` | Take a **type** (not an expression) and return `i64`; `alignof(enum)` is always 4 |
| `type X = ...` | **No trailing semicolon** (with `;` it reports `unexpected token ';' in expression`) |
| Aggregate equality | `struct` / `enum` / arrays / slices are compared **by value**; a slice compares only its **head** (pointer + length), not element by element |
| Aggregate size comparison | `a < b` and the like on aggregate types is a **compile-time error** |
| Overflow | Signed integer overflow is **defined behaviour** (two's-complement wraparound), with no runtime check |

---

## The pre-1.0 boundaries

The spec draws two lines itself: the **body** only documents what is implemented, and **appendix B**
collects every gap.

### Explicit gaps (not implemented)

| Area | Gap |
|---|---|
| Types | `()` in type position; the `fn(...)` function pointer type syntax (⇒ a closure cannot be passed as a function value) |
| Borrows | Full NLL / Polonius borrow checking, lifetime annotations `'a`, reborrow, borrows across functions |
| Closures | Capturing outer variables — **an explicit compile-time error**, no silently generated wrong code |
| Expressions | Block expressions (`let v = { ... };`); a match arm whose body is a statement block |
| Generics | Constraints `<T: Ord>`, lifetime generics, const generics, trait objects, HKT |
| FFI | Variadic functions, callback functions, struct / enum by value across the FFI boundary |
| `Cap<T>` | Field access (`.cnode_idx` / `.depth` / `.rights`); `T` itself is **not parsed** |
| Standard library | The f32 versions of `std::math` and `tan` / `log` / `exp` / `floor` / `ceil` |
| Other | async / await, `std::map`, aarch64 / riscv64, the `.jhyynb` native binary format, the operand constraints of `asm!` and Intel syntax, guard patterns in match, the exponent form for floats |

### Implemented but limited (easy to misjudge as a bug)

| Item | Symptom |
|---|---|
| The type of `argv` | It is written `*u8`, but it is actually `char **` ⇒ `*argv` only loads 1 byte; to read `argv[i]` you must first do `argv as **u8` |
| Operands of aggregate `==` | **The result of a function call** is not accepted (`make_p(1) == make_p(2)` is a compile-time error); storing it in a variable first with `let a = ...;` is safe |
| Fields omitted from a struct literal | They are **uninitialized** (garbage on the stack), **not 0**; the compiler does not report a "missing field" either |
| The type of a struct literal field value | It must **exactly match** the field type — writing `7` (inferred as `i32`) in a `u8` field reports `field type mismatch` |
| Write protection of immutability | Not implemented — `&x` on an immutable binding is legal, and `*p = v` neither reports an error nor **takes effect** |
| Function argument types | **Not checked** — passing an `i32` to a struct parameter compiles, and at runtime the registers are read with the struct layout ⇒ access violation crash |
| Top-level global variables | Only **integer-typed** initializers are evaluated correctly; `f64` reads 0, pointers / structs read garbage |
| `const` elements | No const checking — a function call in an element position is not evaluated, and you get 0 at runtime |
| `match` ranges | Closed intervals (the opposite of `for`) |
| `defer` | Does not cover the implicit return path |
| Nested patterns | Beyond the second level they are **not supported** (rejected at compile time); the outer tag comparison and the inner payload extraction are both not implemented |

The complete item-by-item list is in **appendix B** of the spec; the entries that carry a ledger
number are in
[`docs/internal/workarounds.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/workarounds.md).

---

## How spec changes go through

The spec is a **locked contract** — not a document you edit casually.

- Any change goes through the [RFC process](/compiler/governance/index.html#rfc), it does not edit `docs/abis/` directly.
- Locking is more than tagging a release: every "implemented" item in the body of the spec has to find its implementation in `compiler/src0/*.jhyy` — **the self-hosted compiler is the biggest consumer of the spec**.
- After a change to `docs/abis/*` you have to run the regression suite once (a spec change may affect parsing on the JHYY side).

---

## The original

- Language spec v{{spec_version}} (locked) —
  [`docs/abis/jhyy-lang-spec-v4.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md)
- Companion ABI v{{abi_version}} (locked) —
  [`docs/abis/jhyy-abi-v4.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-abi-v4.0.0.md)
- The archived old versions (v1.3.0 and its 17 v3.x supplements) exist only in git history:
  `git show <sha>:docs/abis/<name>`
