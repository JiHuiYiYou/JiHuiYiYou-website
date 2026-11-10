---
title: Arena 内存管理
description: arena 的心智模型、真实 API、生命周期与常见误用
layout: docs
project: compiler
zone: docs
---

JHYY 的 `arena` 是一个 **bump allocator（撞针分配器）**：分配就是把游标往前推，
释放就是什么都不做。但它**不是**那种「只有 alloc、没有 free」的 arena —— 同一套
API 里既有复位（`arena_reset`，复用内存）也有整块释放（`arena_free`）。这页把它的
真实签名、内存布局、生命周期和几个会咬人的地方摊开。

先说最要紧的一句：**JHYY 有两个 arena，编译器内部用的那一份和你 `import arena;`
拿到的那一份不是同一个东西。** API 等价、实现独立、互不 import。第 3 节讲清楚
怎么区分。

---

## 1. 心智模型

一次分配做三件事：

1. 看当前块剩下的空间够不够；
2. 不够就新开一块（底层是 libc `malloc`）；
3. 把游标 `cur` 推过去，返回对齐后的指针。

| 操作 | 内存发生了什么 |
|---|---|
| `arena_alloc` / `arena_calloc` | 游标前进；不够就新开一块 |
| `arena_reset` | 游标**回退**；**不释放**任何块，内存留着复用 |
| `arena_free` | 遍历链表**逐块 `free`**；之后 arena 的指针字段归零 |

没有 GC，没有析构函数，没有引用计数。**谁分配，谁负责决定它什么时候失效。**

---

## 2. 真实 API

真相源是 `compiler/src0/std/arena.jhyy`，签名逐字抄：

```jhyy
type Arena = struct {
    start:    *u8,
    cur:      *u8,
    end:      *u8,
    blocks:   *u8,         // *ArenaBlock head (使用处 cast)
    def_size: i64,
}
```

| 函数 | 签名 | 返回 |
|---|---|---|
| `arena_init` | `fn arena_init(a: *Arena, default_size: i64) -> i32` | 恒为 `1` |
| `arena_alloc` | `fn arena_alloc(a: *Arena, size: i64) -> *u8` | 8 字节对齐的指针；**失败返回 `0`** |
| `arena_calloc` | `fn arena_calloc(a: *Arena, size: i64) -> *u8` | 同上，且**整段清零** |
| `arena_reset` | `fn arena_reset(a: *Arena) -> i32` | 恒为 `1` |
| `arena_free` | `fn arena_free(a: *Arena) -> i32` | 恒为 `1` |

同一个模块里还有 `arena_alloc_aligned(a, size, align)`、`arena_new_block`、
`align_up`、`ptr_add`（语言规范 § 15 的模块表把它们也列在 `arena` 名下）。

几个必须知道的细节：

- **对齐**：`arena_alloc` 内部就是 `arena_alloc_aligned(a, size, 8)` ⇒ 保证 **8 字节对齐**。
- **失败**：`malloc` 失败时 `arena_alloc` 返回空指针 `0`。**不 panic、不抛错**，调用方必须自己判。
- **`size == 0`**：`arena_alloc(a, 0)` 直接返回 `0`；`arena_calloc(a, 0)` 因此也返回 `0` —— 不是一块合法的零长内存。
- **`arena_init` 的 `default_size`**：`<= 0` 时按 **1 MB（1048576 字节）**记进 `def_size`。
- **返回码基本没信息量**：`init` / `reset` / `free` 恒返回 `1`。真正需要判断的只有 `alloc` / `calloc` 的空指针。

`Arena` 的字节布局（源码注释里写着）：`start`(8) + `cur`(8) + `end`(8) + `blocks`(8) +
`def_size`(8) = **40 字节**。`blocks` 是链表头 —— JHYY 不支持自引用 struct，所以它在
源码里占位成 `*u8`，使用处再 cast。

---

## 3. 两个 Arena 并存

| | 编译器内部那份 | 用户侧标准库那份 |
|---|---|---|
| 文件 | `compiler/src0/arena.jhyy` | `compiler/src0/std/arena.jhyy` |
| 谁在用 | 编译器自己（AST / IL / codegen 节点全在里面） | 你的程序：`import arena;` |
| 块头大小 | 16 字节 | 8 字节 |
| 分块大小 | `max(def_size, 本次请求 + 对齐量)` | `本次请求 + 对齐量`（**完全不看 `def_size`**） |
| 额外函数 | 多一个 `arena_strdup` | 无 |

**为什么分开**（源码注释原话）：内部 jhyy-side 实现不 import `src0/arena.jhyy`，
**避免 mangle 复杂度**；两个 Arena 并存 —— compiler 用 `src0/arena.jhyy`，
std lib user 用 `std::Arena`。

**怎么区分**：`import arena;` 的查找顺序是 **main 文件旁边 → 标准库目录**（两级回落）。

- 编译器自举时 main 文件是 `compiler/src0/main.jhyy`，旁边就有 `arena.jhyy` ⇒ 编译器拿到内部那份。
- 你的程序旁边没有 `arena.jhyy` ⇒ 落到标准库目录 ⇒ 拿到 `std/arena.jhyy` 那份。

你不需要在代码里区分这件事，但**要知道你拿到的不是编译器内部那份** —— 两者的分块
策略不一样，而这一点会直接影响 `arena_reset` 的行为（见 5.1）。

---

## 4. 增长策略：M0 简化

源码注释原话：

> 后端 alloc 走 libc malloc（M0 简化，MMAP 后端留 v3.x 中末）

也就是说：**底层就是 libc `malloc`**。没有 mmap、没有页分配、没有大页。MMAP 后端
是后来的版本才计划的事，现在没有。

由此带来一个反直觉的实测结果：`arena_init(&a, 65536)` **并不预分配 64 KB**。
实测第一个块的数据区只有 **16 字节**（= 8 字节请求 + 8 字节对齐量）。

`def_size` 在标准库那份实现里**只被 `arena_reset` 用到** —— 分配路径完全不看它。

---

## 5. 一个完整的生命周期

```jhyy
import arena;

fn main_jhyy() -> i32 {
    // 1. init：只记录 def_size，不预分配内存
    let mut a: Arena = Arena { start: 0 as *u8, cur: 0 as *u8, end: 0 as *u8,
                               blocks: 0 as *u8, def_size: 0 as i64 };
    arena_init(&a, 65536 as i64);

    // 2. alloc：8 字节对齐；失败返回 0，必须判
    let p = arena_alloc(&a, 8 as i64);
    if p == (0 as *u8) { return 1 as i32; }
    *(p as *i32) = 42 as i32;

    // 3. calloc：分配 + 整段清零
    let z = arena_calloc(&a, 16 as i64);
    if z == (0 as *u8) { return 2 as i32; }

    // 4. use：数据一直有效，直到 reset / free
    let v = *(p as *i32);

    // 5. free：释放全部 block；之后任何旧指针都是悬垂指针
    arena_free(&a);
    return v;
}
```

模块里的函数也可以用限定名调用：`arena::arena_init(&a, 65536)`、
`arena::arena_alloc(&a, 8)` —— 两种写法等价。

### 5.1 reset 的两个反直觉之处

**一、reset 回到的是「最新那块」的起点，不是 arena 的起点。**
源码里 `blocks` 是栈式链表（新块挂到表头），`arena_reset` 取的是表头那块。实测：
先 `alloc(8)`，再 `alloc(4096)`（触发新块），`reset` 之后再 `alloc(8)` 拿到的是
**4096 那块**的地址，不是第一次那块。更早的块仍然挂在链表上（`arena_free` 时
才会一起释放），但 reset 之后不会再分配到它们。

**二、reset 之后的可用窗口曾经按 `def_size` 算 —— v4.1.5 已修。**
`arena_reset` 曾经把 `end` 设成 `start + def_size`，而实际块大小是「请求 + 对齐量」。
`def_size` 更大时，arena 会「以为」自己有一大块可用。

实测后果（`arena_init(&a, 65536)` → `alloc(8)` → `reset` → `alloc(4096)` → 写满
4096 字节）：`alloc(4096)` 返回的指针落在实际块**之外**；进程退出时被 Windows 报
**HEAP_CORRUPTION**（`0xC0000374`）。

**触发区间是确定的**：分配尺寸落在 `(真实块大小, def_size]` 之间就会越界，
两端反而安全——所以这个坑很容易漏掉。

| 场景（`arena_init(&a, 1024)` → `alloc(8)` → `reset` → 分配 N 并写满 N 字节） | v4.1.4 及以前的结果 |
|---|---|
| N = 16 / 32 / 64 | 通过（真实块 16 B + 堆余量够用） |
| N = 128 / 256 / 500 / 1000 / 1024 | **越界 —— 段错误 / HEAP_CORRUPTION** |
| N = 2000 | 通过（超过 `def_size`，走新建块路径） |
| 同样程序**去掉** `reset` | 全部通过 |

**v4.1.5 的修法**：块大小改成 `max(def_size, 请求大小)`，并**记进块头**
（`payload_size`）⇒ `arena_reset` 从块头读回真实大小，不再越界。台账 W-222。

同版还补上了这块的**测试覆盖**：`std::arena` 此前**零测试覆盖** ——
`compiler/tests/examples/arena_reset.jhyy` 是 inline 副本，而且实现更简单
（只重置 `cur`、不碰 `end`）⇒ 真身从没被测过。现在有
`compiler/tests/examples/std_arena_reset/std_arena_reset.jhyy`，
它**必须**待在「没有本地 `arena.jhyy`」的目录里，否则 `import arena;`
会命中那份副本。

### 5.2 安全用法

- 只有在**后续所有分配都不超过 reset 前那块的实际大小**时，`arena_reset` 才是安全的。
- 想要「整轮重来」，最省心的是 **`arena_free` + `arena_init`**，不依赖 reset 的窗口语义。
- `arena_free` 之后 arena 的四个指针字段全部归零（`def_size` 保留）。**free 之后继续用旧指针 = 悬垂指针**，JHYY 没有 GC 也没有自动析构来救你。

### 5.3 什么时候 reset、什么时候 free

| 场景 | 用哪个 |
|---|---|
| 一轮性的临时数据（解析、编译中间态） | `arena_free` |
| 每轮复用同一块内存（注意 5.1 的窗口约束） | `arena_reset` |
| 进程退出 | `arena_free` |
| 需要跨阶段存活的数据 | **别放 arena 里** —— 用 `malloc` 或 `Vec` |

### 5.4 arena、Vec、malloc 怎么选

标准库里另有两个可选方案：`import vec;`（`Vec<T>`，24 字节 `{data, len, cap}`，
配 `std_vec_new` / `std_vec_push` / `std_vec_get` / `std_vec_free`）和
`extern fn malloc` / `free`。

| | arena | `Vec<T>` | `malloc` / `free` |
|---|---|---|---|
| 分配单位 | 整块 bump 推进 | 逐元素 push，自动扩容 | 逐次 |
| 释放粒度 | 整块（`arena_free`）或复用（`arena_reset`） | 整个 Vec（`std_vec_free`） | 每次分配自己管 |
| 越界检查 | 无 | `std_vec_get` 越界返回空指针 | 无 |
| 适合 | 一轮性的、成批的临时对象 | 长度会变的序列 | 单个对象、要交给 C 的缓冲 |

JHYY 没有 GC、没有析构函数、没有 `drop`。**选错了不会报错，只会在某个时刻读到
垃圾或崩掉。**

---

## 6. 和内联汇编 / DMA / MMIO 的关系

源码和 ABI 里**没有** arena 与这三者的专门约定。下面是基于「arena 底层就是 libc
`malloc`」这个事实的**推论**，标出来是为了让你知道边界在哪。

| 场景 | 结论 |
|---|---|
| 内联汇编里用 arena 的指针 | 可以。指针是 8 字节对齐的普通内存地址。但 `asm!` 只接受单个字符串字面量，没有操作数约束、没有 clobber 声明 ⇒ 只能靠 `volatile` 变量或固定地址传递 |
| MMIO 寄存器 | **不行**。arena 给的是进程虚拟地址里的普通内存，MMIO 要的是设备地址。要用 `volatile i32` 配一个固定地址（`extern` 声明的符号） |
| DMA 缓冲 | **不行**（当前）。DMA 要的是设备可见的物理地址 / pinned 内存；arena 给的是可分页、可能被内核搬走的普通堆内存。要做 DMA 得自己写分配器 |

---

## 7. 反模式

| 反模式 | 后果 |
|---|---|
| **跨 arena 引用**：arena A 里的结构体持有 arena B 里的指针 | `arena_free(B)` 之后 A 里那个指针悬垂。两个 arena 之间没有任何共同的存活期约定 |
| **arena 销毁后使用** | 悬垂指针。JHYY 不报错，运行时才崩 |
| **把长期存活的数据分配在马上要 reset 的 arena 里** | reset 之后那些数据全被覆写 —— arena 里**没有**「哪些数据是长期」的标记 |
| **在闭包里用 arena 句柄** | **编译器直接拒绝**：JHYY 的闭包不支持捕获，捕获是编译错误。真正写得出来的变体是把 `*Arena` 存进结构体或全局再在别处用 —— 那还是逃逸 |

---

## 8. 相关页面

- [标准库](/compiler/docs/stdlib.html) —— {{stdlib_modules}} 个模块的 API 总表。
- [语言规范 v{{spec_version}}](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md) —— § 15 是模块 API 表，附录 B 是未实装项。
- [ABI v{{abi_version}}](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-abi-v4.0.0.md) —— § 4.3 说明「编译器自身不实现堆」。
