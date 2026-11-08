---
title: 标准库
description: 八个模块的真实 API：arena、mem、string、vec、fmt、io、math、os
layout: docs
project: compiler
zone: docs
---

# 标准库

JHYY 自带一份小标准库，**8 个模块**，随编译器一同安装。
本页的每个签名都是从源码逐字抄的——`compiler/src0/std/*.jhyy`——
没有改写，也没有补全源码里不存在的函数。

> **源码是唯一真相源**：
> [`compiler/src0/std/`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/tree/main/compiler/src0/std)

---

## 怎么用

`import` 拉进来的是**模块**，**不带 `std::` 前缀**——`import std::vec;` 是解析错误：

```jhyy
import io;
import vec;

fn main_jhyy() -> i32 {
    io::std_io_print("hello from the JHYY stdlib\n");
    0
}
```

两种调用写法都实测能编过：

| 写法 | 出处 |
|---|---|
| `io::std_io_print(...)` | 仓库 README、`compiler/tests/examples/std_io_import.jhyy` 用的就是这一种 |
| `std_io_print(...)` | 规范 § 15 指定的写法（直接写源码里的函数名） |

⚠ 规范 § 15 只承认后一种——它明确说「不是 `io::std_io_print(...)`」；
但限定写法在实现里是通的，仓库自己的 README 和回归用例走的就是它。
两种都不会报 `undefined variable`。**推荐限定写**——`ptr_add` 这类名字
在多个模块里各有一份（见下表），不限定容易指错。

命名风格**历史上不统一**：

| 风格 | 模块 | 例 |
|---|---|---|
| `<mod>_<fn>` | `mem` / `fmt` / `string` / `arena` | `mem_copy`、`fmt_i32`、`str_concat`、`arena_alloc` |
| `std_<mod>_<fn>` | `io` / `os` / `vec` / `math` | `std_io_print`、`std_os_exit`、`std_vec_new`、`std_math_sin` |

写错名字的报错是 `undefined variable`——**没有**「你是不是想写 …」的提示。
第一次用某个模块时，照着下面的表抄名字。

| 模块 | 解决什么问题 |
|---|---|
| [`mem`](#mem) | 裸内存的拷贝、清零、比较、查找 |
| [`fmt`](#fmt) | 把整数 / 字符串格式化进字节缓冲区 |
| [`string`](#string) | 带长度前缀的 UTF-8 字符串 |
| [`vec`](#vec) | 动态字节数组 |
| [`arena`](#arena) | bump 分配器——一次性申请、整块复用 |
| [`io`](#io) | 文件句柄与读写、标准输出 / 错误输出 |
| [`os`](#os) | 裸文件描述符、进程退出、环境变量 |
| [`math`](#math) | 三角、平方根、幂（**只有 f64**） |

---

## mem

**解决什么问题**：裸内存操作。全部是自实现的 byte 循环——**不调 libc**，
所以标准库本身不依赖 libc 运行时。

| 签名 | 做什么 |
|---|---|
| `fn ptr_add(p: *u8, off: i64) -> *u8` | 本地指针算术 helper |
| `fn mem_copy(dst: *u8, src: *u8, n: i64) -> *u8` | 复制 n 字节；返回 `dst` |
| `fn mem_compare(a: *u8, b: *u8, n: i64) -> i32` | 比较 n 字节：`0` equal / `<0` a<b / `>0` a>b |
| `fn mem_set(dst: *u8, val: i32, n: i64) -> *u8` | n 字节设为 `val`（低 8 位）；返回 `dst` |
| `fn mem_find_byte(p: *u8, n: i64, val: i32) -> i64` | 找第一个 `== val` 的字节；返回 index / `-1` |
| `fn mem_zero(dst: *u8, n: i64) -> *u8` | n 字节清零；返回 `dst` |

**坑**

- ⚠️ **`mem_copy` 不处理 overlap**——语义跟 libc `memcpy` 一致。
  重叠区要拷得用 `memmove`，**本模块不实现**。
- 失败语义：长度 `< 0` 返 `0` / null（不允许）；长度 `0` 是 no-op。
- ⚠️ **`mem_set` 假设 `dst` 是 8 字节对齐**。`std::arena` 的 `arena_alloc` 保证这一点，
  但**外部 caller 不保证**——非 8 对齐的 `dst` 会触发 i64 store 的 `#GP`。
- `mem_set` 走 i64-store 批量写 + i32-store 尾段（W-075 真修）。
  更早的版本用 `*i32` 宽度写 1 字节步进的循环，**请求 n 字节实际写 4n 字节**，
  多出来的部分踩掉调用方的缓冲区（W-139 已修）。

---

## fmt

**解决什么问题**：把值格式化成字节。自实现，不走 libc `printf` 的变参 ABI。

| 签名 | 做什么 |
|---|---|
| `fn ptr_add(p: *u8, off: i64) -> *u8` | 本地指针算术 helper |
| `fn digit_char(d: i32) -> i32` | 0–9 → ASCII 码 |
| `fn hex_char(d: i32, upper: i32) -> i32` | 0–15 → ASCII 码；`upper != 0` 时用大写 `A`–`F` |
| `fn fmt_i32(out_buf: *u8, val: i32) -> i64` | 写 i32 十进制；返回写入字节数（不含 `\0`） |
| `fn fmt_i64(out_buf: *u8, val: i64) -> i64` | 写 i64 十进制；返回字节数 |
| `fn fmt_str(out_buf: *u8, s: *u8) -> i64` | 复制 cstr 到 `out_buf`；返回字节数 |
| `fn fmt_hex_u32(out_buf: *u8, val: i32, upper: i32) -> i64` | 写 u32 十六进制（无 `0x` 前缀）；返回字节数 |

**坑**

- ⚠️ **`out_buf` 必须 ≥ 32 字节。** i32 最多 11 位 + sign + `\0`，
  i64 最多 20 位 + sign + `\0`，hex u32 最多 10 位 + `\0`。
- ⚠️ **没有浮点格式化。** `fmt` 里没有 `f32` / `f64` 的格式化函数。
- ⚠️ **`fmt_hex_u32` 的 `val` 是 u32 的位模式、以 `i32` 传入。**
  值 ≥ `0x80000000` 时它是**负的**——函数内部手工转成无符号的 `i64` 再算。
- `fmt_i32` / `fmt_i64` 用**向 0 截断**的除法，不取绝对值，
  所以 `i32::MIN` / `i64::MIN` 天然可用（W-195 真修）。
  更早的版本先取绝对值，`MIN` 取负回绕成它自己 ⇒ 只打出一个 `-`。

---

## string

**解决什么问题**：带长度前缀的 UTF-8 字符串。字符串用**裸 `*u8` + 长度**表示
（跟 `CapTable` 路径一致），**不是**借用（`&str` 还没做）。

| 签名 | 做什么 |
|---|---|
| `fn ptr_add(p: *u8, off: i64) -> *u8` | 本地指针算术 helper |
| `fn strlen_local(s: *u8) -> i64` | cstr 长度 |
| `fn str_from_cstr(a: *u8, s: *u8) -> *u8` | 复制 cstr 到 arena；返回 `*StringHeader` |
| `fn str_from_bytes(a: *u8, p: *u8, n: i64) -> *u8` | 复制 n 字节；返回 `*StringHeader` |
| `fn str_len(s: *u8) -> i64` | 长度 |
| `fn str_data(s: *u8) -> *u8` | data 指针（**不保证 NUL 结尾**） |
| `fn str_concat(a: *u8, x: *u8, y: *u8) -> *u8` | 拼接 x + y 到新 arena buffer；返回 `*StringHeader` |
| `fn str_equals(x: *u8, y: *u8) -> i32` | `1` equal / `0` |
| `fn str_compare(x: *u8, y: *u8) -> i32` | 字典序：`0` equal / `<0` x<y / `>0` x>y |
| `fn str_find(s: *u8, needle: *u8) -> i64` | 找子串（needle 必为 cstr）；index / `-1` |
| `fn STR_HEADER_SIZE() -> i64` | `StringHeader` 字节数（16） |

`StringHeader` 的布局是 `data: *u8` + `len: i64`，共 16 字节。

**坑**

- ⚠️ **buffer 不强制 NUL 结尾**（M0 简化）。需要时自己写 `*(data + len) = 0`。
- ⚠️ **所有 string buffer 从模块内部的 mini-arena 分配**——caller 自己负责
  `reset` / `free`。这个 mini-arena 是 `string.jhyy` **内嵌**的，
  不复用 `std::arena` 模块。
- ⚠️ **模块内部另有 4 个同名函数**：`arena_init` / `arena_alloc` / `arena_reset` /
  `arena_free`，签名都是 `*u8`（不是 `*Arena`）。
  它们和 `std::arena` 模块的同名函数**并存，且不报重定义错误**——
  不限定写会解析到其中一个。要确定调用的是哪一个，用 `string::` / `arena::` 限定。
- `str_find` 的 `needle` 必须是 **cstr**（内部用 `strlen_local` 量长度）。
- 历史坑：block 布局曾是 `[next(8B)][payload...]`，payload 起点压在 next 指针那一格上
  ⇒ 第一次分配的字节直接覆盖 block 的 next 指针，链表当场损坏，且 bump 指针不推进
  ⇒ 连续分配两个以上字符串就会 ACCESS_VIOLATION（W-141 已修成
  `[next(8B)][payload_size(8B)][payload...]`）。

---

## vec

**解决什么问题**：动态数组。

⚠️ **先说清楚一件事：`Vec` 不是泛型容器。** 它的 `elem_size` 是**运行时参数**，
不是一个类型参数。

| 签名 | 做什么 |
|---|---|
| `fn std_vec_new(elem_size: i64) -> Vec` | 空 Vec（`data`/`len`/`cap` 全 0） |
| `fn std_vec_with_cap(elem_size: i64, cap: i64) -> Vec` | 预分配 cap 个 slot；`elem_size ≤ 0` 或 `cap ≤ 0` 返空 Vec |
| `fn std_vec_push(v: *Vec, elem_size: i64, src: *u8) -> i32` | 追加 1 个元素（从 `src` 拷 `elem_size` 字节）；返 1 成功 / 0 OOM |
| `fn std_vec_get(v: *Vec, elem_size: i64, idx: i64) -> *u8` | 元素指针；**越界返回 NULL** |
| `fn std_vec_len(v: *Vec) -> i64` | 元素数 |
| `fn std_vec_cap(v: *Vec) -> i64` | 已分配的 slot 数（**不是字节数**） |
| `fn std_vec_free(v: *Vec) -> i32` | 释放 data buffer 并重置 |
| `fn std_vec_grow(v: *Vec, elem_size: i64, new_cap: i64) -> i32` | 私有 helper：cap 翻倍直到 ≥ `new_cap` |
| `fn std_vec_byte_copy(dst: *u8, src: *u8, n: i64) -> *u8` | 私有 helper：拷 n 字节 |
| `fn VEC_SIZE() -> i64` | `Vec` 字节数（24） |
| `fn ptr_add(p: *u8, off: i64) -> *u8` | 本地指针算术 helper |

`Vec` 的布局是 `data: *u8` + `len: i64` + `cap: i64`，共 24 字节。

**坑**

- ⚠️ **`std_vec_get` 返回的是指针，不是元素值**——因为 `elem_size` 是运行时参数，
  caller 拿到指针后自己解引用。
- ⚠️ **`std_vec_push` 不检查 `src` 是否为 NULL**——它会按 `elem_size` 从 `src` 读。
  传空指针进去就是读空地址。
- `std_vec_new` 返回的是 **24 字节 struct 值**（不是指针）——源码注释写明这是为了
  避开 sret 的 ABI 复杂度。
- **不依赖完整的 drop 语义**（leak-OK）：没有自动析构，`std_vec_free` 要自己调。
- `std_vec_with_cap` 里的 `malloc` 失败检查是 2026-11-07 补的——补之前它会返回
  `data=NULL` 的 Vec，caller 之后往里写 ⇒ 写 NULL 地址 ⇒ 进程直接崩。

---

## arena

**解决什么问题**：bump 分配器。一块一块地申请内存、在块内线性推进指针，
需要时整块复用或整块释放。

> **展开讲**：[Arena 内存管理](/compiler/docs/arena.html) —— 分配器模型、
> 与 GC 的取舍、什么时候该用它。

| 签名 | 做什么 |
|---|---|
| `fn arena_init(a: *Arena, default_size: i64) -> i32` | 初始化；`default_size ≤ 0` 时用 1 MB。返 1 |
| `fn arena_alloc(a: *Arena, size: i64) -> *u8` | 8 字节对齐分配；失败返 0 |
| `fn arena_alloc_aligned(a: *Arena, size: i64, align: i64) -> *u8` | 指定对齐的分配；`size == 0` 返 0 |
| `fn arena_calloc(a: *Arena, size: i64) -> *u8` | 分配并清零 |
| `fn arena_reset(a: *Arena) -> i32` | 重置游标到起点，**不释放 block** |
| `fn arena_free(a: *Arena) -> i32` | 释放所有 block |
| `fn arena_new_block(a: *Arena, size: i64) -> i32` | 私有：新建一块并挂到链表头 |
| `fn align_up(x: i64, align: i64) -> i64` | 把 x 上调到 align 的倍数（align 须为 2 的幂） |
| `fn ptr_add(p: *u8, off: i64) -> *u8` | 本地指针算术 helper |
| `fn ARENA_SIZE() -> i64` | `Arena` 字节数（40） |
| `fn ARENA_BLOCK_HEADER() -> i64` | block 头字节数（8） |

`Arena` 的布局是 `start` / `cur` / `end` / `blocks`（都是 `*u8`）+ `def_size: i64`，共 40 字节。

**坑**

- ⚠️ **`arena_reset` 会把可用空间算成 `def_size`（默认 1 MB），但实际 block 没那么大。**
  `arena_init` 只记录 `def_size`、**不分配任何 block**；真正的 block 是
  `arena_alloc` 触发的，尺寸是 `size + align`，**不是** `def_size`。
  `arena_reset` 却把 `end` 设成 `start + def_size` ⇒ arena 以为自己有 1 MB 可用，
  实际脚下只有几十字节 ⇒ **后续分配会写穿 malloc 出来的块**。

  **触发条件是分配尺寸落在 `(真实 block 大小, def_size]` 这个区间里。**
  实测（2026-11-08，v4.1.4 自举编译器，本机）：

  | 场景 | 结果 |
  |---|---|
  | `alloc(8)` → `reset` → `alloc(16/32/64)` | 通过（真实块 16B + 堆余量够用） |
  | `alloc(8)` → `reset` → `alloc(128/256/500/1000/1024)` | **ACCESS_VIOLATION（段错误）** |
  | `alloc(8)` → `reset` → `alloc(2000)` | 通过（超过 `def_size`，走新建块路径） |
  | 同样程序**去掉** `reset` | 全部通过 |

  ```jhyy
  import arena;

  fn main_jhyy() -> i32 {
      let mut a: Arena = Arena {
          start: 0 as *u8, cur: 0 as *u8, end: 0 as *u8,
          blocks: 0 as *u8, def_size: 0 as i64,
      };
      arena_init(&a, 1024);
      let p = arena_alloc(&a, 8);
      arena_reset(&a);                    // ← end 被设成 start + 1024
      let big = arena_alloc(&a, 500);     // ← 以为有 1 MB，实际脚下只有 16 B
      let mut i: i32 = 0;
      while i < 500 { *(big + i as i64) = 1 as u8; i = i + 1; }   // ← 写穿
      0
  }
  ```

  两端都安全，所以这个坑很容易漏掉：小分配塞得下，超大分配会另开一块，
  只有「中等大小 + reset 之后」这一档会炸。
  （编译器自用的那份 arena——`compiler/src0/arena.jhyy`——block 尺寸取
  `max(def_size, min_size)`，没有这个问题；**两份实现的行为不一致**。）
  **这条目前不在问题台账里。**
- `blocks` 字段走 `*u8` 占位（JHYY 不支持自引用 struct），使用处要 cast 成
  `*ArenaBlock`。
- `arena_alloc_aligned` 与 `arena_new_block` 在源码注释里标为**私有 API**——
  它们是 `fn`（所以公开可见），但不打算让你直接用。
- 底层走 libc `malloc`（M0 简化；MMAP 后端留在 v3.x 中末）。
- **怎么拿到一个 `Arena` 实例**：`arena::Arena { ... }` 这种**限定名的 struct 字面量
  解析不了**。可行做法是本地声明一个同布局的 struct 再 cast 指针
  （`&local as *arena::Arena`），或自己 `malloc` 40 字节清零后 cast。

---

## io

**解决什么问题**：文件句柄与读写，加上标准输出 / 错误输出。
后端走 libc 的 `fopen` / `fread` / `fwrite` / `fclose`。

| 签名 | 做什么 |
|---|---|
| `fn std_io_open(path: *u8, mode: *u8) -> *u8` | 打开文件（`mode` 是 cstr：`"r"` / `"w"` / `"wb"` / `"rb"` / `"a"` …）；返回 `FILE*` / 失败返 0 |
| `fn std_io_close(f: *u8) -> i32` | 关闭；`f == 0` 返 `-1`，否则返 `fclose` 的结果 |
| `fn std_io_read(f: *u8, buf: *u8, n: i64) -> i64` | 读 n 字节到 `buf`；返实际字节数（`< n` 表示 EOF / error） |
| `fn std_io_write(f: *u8, buf: *u8, n: i64) -> i64` | 写 n 字节；返实际写出的字节数 |
| `fn std_io_print(s: *u8) -> i32` | 写 stdout（cstr）；`s == 0` 返 `-1` |
| `fn std_io_print_err(s: *u8) -> i32` | 写 stderr（cstr）；`s == 0` 返 `-1` |
| `fn std_io_eprint(s: *u8) -> i32` | `std_io_print_err` 的别名 |

**坑**

- ⚠️ **`std_io_print` / `std_io_print_err` 依赖 libc 的 `stdout` / `stderr` 句柄获取**
  （走 C 侧的 `jh_fputs_stdout` / `jh_fputs_stderr` 桥）。这意味着用了它们就
  **依赖 C 运行时**——与 `no_std` 方向冲突。
- `std_io_read` / `std_io_write` 在 `f == 0` 时返 `-1`，`n <= 0` 时返 `0`。
- 源码注释写明：OS kernel M11 launch 后要换成 syscall 实现
  （改 `jhyy_helpers.c` 里的 `jh_fputs_*`），**`std/io.jhyy` 一行都不用动**。

---

## os

**解决什么问题**：裸文件描述符、进程退出、环境变量。

| 签名 | 做什么 |
|---|---|
| `fn std_os_open(path: *u8, flags: i32, mode: i32) -> i64` | `open(2)` wrapper；返 fd / 失败返 `-1` |
| `fn std_os_close(fd: i64) -> i32` | `close(2)` wrapper；`0` ok / `-1` fail |
| `fn std_os_read(fd: i64, buf: *u8, n: i64) -> i64` | `read(2)` wrapper；返字节数，EOF 返 0，出错返 `-1` |
| `fn std_os_write(fd: i64, buf: *u8, n: i64) -> i64` | `write(2)` wrapper；返写出的字节数，出错返 `-1` |
| `fn std_os_exit(code: i32)` | 终止进程（**真退出**，never returns） |
| `fn std_os_getenv(name: *u8) -> *u8` | 读环境变量；返值 cstr / 未找到返 0 |
| `fn OS_O_RDONLY() -> i32` | `0` |
| `fn OS_O_WRONLY() -> i32` | `1` |
| `fn OS_O_RDWR() -> i32` | `2` |
| `fn OS_O_CREAT() -> i32` | `64`（`0x40`） |
| `fn OS_O_TRUNC() -> i32` | `512`（`0x200`） |
| `fn OS_O_APPEND() -> i32` | `1024`（`0x400`） |
| `fn OS_MODE_RW_R() -> i32` | `420`（`0644`） |

**坑**

- ⚠️ **`OS_O_*` / `OS_MODE_RW_R` 是零参函数，不是常量。**
  用法是 `os::OS_O_CREAT()`——不带括号会得到 `expected (, got ;`。
- ⚠️ **`O_*` 是 POSIX 值**（`O_CREAT = 0x40`），与 Windows 的 `_O_*`
  （`O_CREAT = 0x100`）不同。平台差异在 C bridge 那一层翻译，jhyy 侧保持 POSIX 语义。
- ⚠️ **`std_os_*` 走 `jhyy_helpers.c` 的 5 个 libc bridge**，所以它们**又依赖 C 运行时**
  ——与「删 C runtime / 0-C 闭环」的方向相反（W-103 登记了这个取舍）。
  真要 0-C 时要换掉的是 bridge 的**实现**，`std/os.jhyy` 一行都不用动。
- `std_os_open` 做输入验证：`path == 0`、`flags < 0`、`mode < 0`、`mode > 0777`
  一律返 `-1`（对齐 libc `open()` 的错误语义）。

---

## math

**解决什么问题**：三角函数、平方根、幂。**只有 f64**。

| 签名 | 做什么 |
|---|---|
| `fn std_math_sin(x: f64) -> f64` | `sin(x)`，x 为弧度 |
| `fn std_math_cos(x: f64) -> f64` | `cos(x)`，x 为弧度 |
| `fn std_math_sqrt(x: f64) -> f64` | `√x`；`x < 0` → NaN，`x = +∞` → `+∞` |
| `fn std_math_pow(base: f64, exp: f64) -> f64` | `base^exp`，libm C99 语义 |

**坑**

- ⚠️ **只有 f64 版本。** 没有 f32，也没有 `tan` / `log` / `exp` / `floor` / `ceil`。
- 直接 FFI 接 libm（Windows 走 MSVCRT，POSIX 走 libc + libm）——`-lm` 已在链接行里。
  **不走 C-side bridge**：后端的 f64 返回走 `%xmm0` + `movsd`，直接 extern 即可。
- 语义跟 libm 一致：finite 输入返 finite 值，`inf` / `NaN` 透传（IEEE 754）。
  **无异常、无 errno**。

---

## 状态

标准库是 **pre-1.0** 的产物，**API 会变**。源码里的版本注释写着
`v3.2.2 (3l.1)` 到 `v3.2.5 (3l.4)`——那是模块自己的一次迭代编号，
不代表任何兼容性承诺。

**这页是人工维护的。** 理想状态是由编译器自己生成标准库文档
（从 `compiler/src0/std/*.jhyy` 抽签名），当前还没有那条流水线——
所以签名有可能和源码漂移。**发现对不上，以源码为准**，然后提个 issue。

相关的坑台账在
[`docs/internal/workarounds.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/workarounds.md)，
语言层面的限制在
[语言规范 v4.0.0](/compiler/docs/spec.html) 的附录 B。
