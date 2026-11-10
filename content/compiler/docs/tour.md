---
title: 语言导览
description: 语言形态速览：类型、过程、模块、FFI
layout: docs
project: compiler
zone: docs
---

# 语言导览

这是导览，不是规范。**语言规范**才是权威——它已锁定，已知限制集中在它的附录 B：
[规范](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md)。

---

## 语言的整体形状

**静态类型。面向表达式。编译成原生代码。**

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

三处值得注意：

- 函数体是**表达式**——最后一个表达式就是返回值。
- `if`、`match` 和块本身也是值，不只是语句。
- 字符串字面量**就是** `*u8`（`.data` 段里以 NUL 结尾的 UTF-8 字节），不需要转换。

---

## 支持什么

| 类别 | 支持 |
|---|---|
| **类型** | `i8/i16/i32/i64`、`u8/u16/u32/u64`、`f32/f64`、`bool`、`*T`、`[T; N]`、`[*]T`（切片）、`struct`、`enum`、`Cap<T>`、`PhantomData<T>` |
| **尺寸** | `sizeof(T)` / `alignof(T)` —— 编译期常量 |
| **转换** | `as` —— 整数/浮点互转、加宽/收窄、`*T ↔ i64/u64` |
| **控制流** | `if`/`else`（有值）、`while`、`for i in start..end`、`break`、`continue`、`match`（字面量/区间/枚举/通配，带穷尽性检查） |
| **清理** | `defer` —— 作用域退出时按 LIFO 执行；隐式尾返回时不执行 |
| **顶层常量** | `const NAME: [T; N] = [...]` —— 编译期落到 `.data` 段 |
| **逻辑** | `&&` / `\|\|` 短路，`!` / `~` 一元 |
| **函数** | 一等函数、递归、复合赋值（`+=` `-=` `*=` `/=` `%=`）、块表达式闭包（不能捕获——捕获是编译错误） |
| **模块** | `import` + 传递导入、多文件 CLI、`mod::fn()` 命名空间 |
| **FFI** | `extern fn` 调 C（printf、文件 I/O、多参数） |
| **OS / 嵌入式** | `#[no_std]`、`#[naked]`、`#[link_section]`、`volatile`、内联 `asm!`、内存屏障 |
| **标准库** | `import mem;` / `fmt` / `io` / `math` / `string` / `vec` / `os` / `arena` —— **注意：没有 `std::` 前缀** |

### 四条最容易被误读的能力

| 能力 | 状态 | 实际意味着什么 |
|---|---|---|
| `[*]T`（切片） | 可用 | 它是数组之上的一个**视图**——写会写回原数组，而且索引**不做越界检查** |
| `PhantomData<T>` | 仅类型层 | 作为 struct 字段合法；但实例化它是编译错误 |
| `asm!` | 受限 | **只能是一个字符串字面量**——没有操作数约束、没有 clobber；AT&T 语法，仅 x86-64 |
| `Cap<T>` | 仅布局 | 8 字节布局是定死且可测的，但目前还造不出值——真正的 capability 语义在路线图上 |

---

## 模块与标准库

`import` 拉进来一个模块。**没有 `std::` 前缀**——`import std::vec;` 是编译错误。

```jhyy
import io;

extern fn puts(s: *u8) -> i32;

fn main_jhyy() -> i32 {
    io::std_io_print("hello from the JHYY stdlib\n");
    puts("and from libc, through extern fn");
    0
}
```

| 模块 | 提供什么 |
|---|---|
| `mem` | `mem_copy` / `mem_set` / `mem_zero` / `mem_compare` / `mem_find_byte` |
| `fmt` | `fmt_i32` / `fmt_i64` / `fmt_str` / `fmt_hex_u32` —— 格式化进字节缓冲区 |
| `io` | 文件 I/O（`std_io_open` / `std_io_read` / `std_io_write` / `std_io_close`）+ `std_io_print` / `std_io_print_err` |
| `math` | `std_math_sin` / `std_math_cos` / `std_math_sqrt` / `std_math_pow` |
| `string` | 带长度前缀的字符串：`str_from_cstr` / `str_concat` / `str_find` / `str_len` |
| `vec` | `std_vec_new` / `std_vec_push` / `std_vec_get` —— 字节向量，**还做不到泛型元素** |
| `os` | 裸的 POSIX / Win32 文件描述符 + `std_os_getenv` |
| `arena` | bump 分配器：`arena_init` / `arena_alloc` / `arena_reset` |

---

## 和 C 打交道

```jhyy
extern fn printf(fmt: *u8, val: i32) -> i32;
```

`extern fn` 按 C ABI 调 C 函数。两条要记住：

- **没有可变参数形式。** 每个 C 参数都得一个一个写出来。
- **参数类型不会跟 C 签名对拍。** 写错了照样编译通过，运行时才出问题。

struct 布局与调用约定见
[ABI 白皮书](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-abi-v4.0.0.md)。

---

## 内存

**没有垃圾回收，也没有 RAII。** 内存归你自己管：

- 显式指针（`*T`）、通过运行时的 arena 或你自己的分配器手动分配；
- 想要的话可以用 `defer` 做作用域退出清理——按 LIFO 执行（但隐式尾返回时不执行）；
- 标准库里有 `arena`，适合的场景直接用。

这是刻意的选择：这门语言面向系统级工作，那里一个可预期的内存模型比便利更重要。

---

## 现在还**没有**的东西

老实列出来——项目是 pre-1.0 的，它自己就这么说：

| 你想…… | 当下 |
|---|---|
| 用带 trait 的泛型 | 还没有 —— 在 OS 线上排着 |
| 用能捕获变量的闭包 | 还没有 —— 今天捕获是编译错误 |
| 打印浮点数 | 还没有 —— `fmt` 里没有浮点格式化 |
| 目标 aarch64 / riscv64 | 还没有 —— 只有 x86-64 |
| 拿它上生产 | 还没有 —— 规范还在动 |

权威清单（带版本）在仓库的
[FACTS.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md)；
逐条限制在规范附录 B。

---

## 接下来

- [[构建与测试]] —— 写点东西并验证它。
- [[常见问题]] —— 关于这门语言的高频问题。
- [[架构]] —— 源码过了解析器之后会去哪里。
