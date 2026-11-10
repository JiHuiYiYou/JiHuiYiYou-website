---
title: ABI v{{abi_version}}
description: 类型布局、调用约定与链接规则——产物之间互认的契约
layout: docs
project: compiler
zone: docs
---

# ABI v{{abi_version}}

**ABI 原文在仓库里，不在这里。**
原文：[`docs/abis/jhyy-abi-v4.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-abi-v4.0.0.md)

本页是那份 ABI 的**导读**：目标与调用约定、类型布局、聚合类型传参、链接规则，
以及一份**已知偏离与未实装项**的摘要。**冲突时以仓库原文为准。**

ABI 锁在 v{{abi_version}}（2026-10-24 随 `v4.0.0 final` 一同锁版），与语言规范同代。
工具链版本是另一回事，见[参考总览](/compiler/docs/reference.html)。

---

## 目标与调用约定

| 目标三元组 | 调用约定 | 运行时 | 状态 |
|---|---|---|---|
| `amd64_win`（默认） | MS x64 | hosted（链 C 运行时） | stable |
| `amd64_sysv` | SysV AMD64 | hosted | stable |
| `amd64_win_freestanding` | MS x64 | freestanding | beta |
| `amd64_sysv_freestanding` | SysV AMD64 | freestanding | beta |

- **架构只有 x86-64。** aarch64 / riscv64 未实装（ABI § 12.10）。
- 四个目标**全部**走自托管 amd64 后端，没有 QBE 回退路径。
- `amd64_win` 与 `amd64_win_freestanding` 的**调用约定逐字节相同**；
  `amd64_sysv` 与 `amd64_sysv_freestanding` 同理。

### MS x64（`amd64_win` / `amd64_win_freestanding`）

| 规则 | 内容 |
|---|---|
| 整型 / 指针参数 | 前 4 个走 `RCX` `RDX` `R8` `R9`，其余走栈 |
| 浮点参数 | 前 4 个走 `XMM0`–`XMM3`，其余走栈 |
| 返回值 | 整型 / 指针 → `RAX`；浮点 → `XMM0` |
| Shadow space | 调用者在栈上预留 32 字节 |
| 栈对齐 | `call` 前 16 字节对齐 |

**整数与浮点实参共享同一个位置计数器**——这是 MS x64 的核心规则：

| 槽位 | 整数寄存器 | 浮点寄存器 |
|---|---|---|
| 1 | `RCX` | `XMM0` |
| 2 | `RDX` | `XMM1` |
| 3 | `R8` | `XMM2` |
| 4 | `R9` | `XMM3` |
| ≥ 5 | 栈 | 栈 |

⇒ `fn f(a: f64, b: i32)` 里 `a` 在 `XMM0`、`b` 在 **`EDX`**（不是 `ECX`）。

### SysV AMD64（`amd64_sysv` / `amd64_sysv_freestanding`）

| 规则 | 内容 |
|---|---|
| 整型 / 指针参数 | 前 6 个走 `RDI` `RSI` `RDX` `RCX` `R8` `R9`，其余走栈 |
| 浮点参数 | 前 8 个走 `XMM0`–`XMM7`，其余走栈 |
| Shadow space | **无** |
| 栈对齐 | `call` 前 16 字节对齐 |

**整数与浮点是两个独立 bank**——整数按出现顺序占 `rdi`/`rsi`/…，
浮点按出现顺序占 `xmm0`–`xmm7`，各自编号、互不影响。
这与 MS x64 的共享计数器**正好相反**：同一个 `fn f(a: f64, b: i32)`，
在 SysV 下 `b` 落在 **`RDI`**。

> 写混合 int / float 参数的函数时，这条差异是最容易出错的地方——
> 纯 JHYY 代码跨目标行为一致（返回值规则相同），但**手写汇编对接**时会踩。

---

## 类型布局

| 类型 | sizeof | alignof | 备注 |
|---|---|---|---|
| `i8` / `u8` | 1 | 1 | 加载到 32 位后符号 / 零扩展 |
| `i16` / `u16` | 2 | 2 | 同上 |
| `i32` / `u32` | 4 | 4 | |
| `i64` / `u64` | 8 | 8 | |
| `f32` | 4 | 4 | IEEE 754 binary32 |
| `f64` | 8 | 8 | IEEE 754 binary64 |
| `bool` | 1 | 1 | ⚠️ 编译器**不做 0/1 归一化** |
| `()` | 0 | 1 | 零大小类型 |
| `*T` | 8 | 8 | 空指针是整数 0；步长 `sizeof(T)` |
| `fn(...)` 函数指针 | 8 | 8 | ⚠️ 类型位置不认这个语法（语言规范附录 B） |
| `[*]T` 切片 | 16 | 8 | `{ data: *T @0, len: i64 @8 }` |
| `[T; N]` | `N × sizeof(T)` | `alignof(T)` | 元素连续，无 padding |
| `&T` / `&mut T` | 8 | 8 | 单指针；`is_mut` 是编译期标记 |
| `Cap<T>` | 8 | 8 | |
| `PhantomData<T>` | 0 | 1 | ZST，不占 struct 槽位 |

- **有符号整数溢出是定义行为**：二进制补码环绕，无运行时检查。
- **没有独立的 `char` 类型**——字符字面量的类型是 `i32`，值是 Unicode codepoint。
- `struct` 按声明顺序排列、**自然对齐**；嵌套 struct 内联展开为单层布局。
- `enum` 的 tag 是 `i32`，offset 0；payload 从 `align_up(4, max_payload_align)` 开始。
- ⚠️ `alignof(enum)` 硬编码返回 **4**，与 enum 布局算出的自然对齐不一致（ABI § 12.2）。

---

## 聚合类型传参

### Win

| 参数类型 | 传递方式 |
|---|---|
| `struct` | 调用者在栈上**建副本**，逐字段复制（含嵌套 struct 递归），传副本地址（一个 `l` 参数） |
| `enum` | 传**一个 `l`**（enum 值自身槽的地址），**不建副本** |
| `[T; N]` | 传**一个 `l`**（数组自身地址），**不建副本**（实质按引用） |
| `[*]T` 切片 | 16 字节槽 `{data, len}`，但**只传一个 `l` 指针**指向该槽 |

⚠️ **只有 `struct` 真正建副本。** `enum` / `[T; N]` / 切片是按地址传递——
所以在 callee 里改数组会改到调用方的数组。

### SysV

| 条件 | 传递方式 |
|---|---|
| `sizeof ≤ 16` | 按 eightbyte 切分分类（INTEGER / SSE），最多 2 个 eightbyte 进寄存器 |
| `sizeof > 16` | **MEMORY class** —— 整体落在栈上 |

### 返回值

| 返回类型 | 约定 |
|---|---|
| 整型 / 指针 / `&T` | `RAX` |
| `f32` / `f64` | `XMM0` |
| `struct` / `enum` | **隐式 sret**：调用者分配返回槽，作为**隐藏的第 0 个参数**在寄存器里传入（Win `%rcx` / SysV `%rdi`） |
| `[T; N]` | ⚠️ **不走 sret**：callee 自建 16 字节槽，`RAX` 返回其地址 |
| `()` | 无返回值，函数尾部裸 `ret` |

### 名称修饰

| 情形 | 符号形式 |
|---|---|
| 普通函数 | `<name>` |
| 模块内函数 | `<mod>__<name>`（调用侧写 `mod::fn()`） |
| 泛型实例 | `<Base>$<T1>$<T2>`（例如 `max$i32`） |
| 模块内泛型实例 | `<mod>__<Base>$<T1>$<T2>`（模块前缀优先） |
| 闭包 | `__closure_<N>`（合成名，N 每次编译单调递增 ⇒ 产物可复现） |
| `extern fn` | **原样**，不加前缀、不加修饰 |

泛型修饰名由 parser 按源码顺序拼出，**不含指针地址或哈希** ⇒ 确定性。
无重载支持。

---

## 程序入口与链接

**这一节是最容易搞错的地方。**

| 模式 | 入口符号 | 说明 |
|---|---|---|
| hosted | `main_jhyy` | C 运行时的 `main` 调用 `main_jhyy(argc, argv)`，其返回值作为进程退出码 |
| `#[no_std]` | `main` | 链接行 `-nostartfiles -nodefaultlibs -Wl,--entry=main -lgcc` |

- `#[no_std]` **不链接 C 运行时启动文件**；`-lgcc` 只提供 `___chkstk_ms` 这类编译器内建。
- `#[no_std]` 模式下 `fn main` **必须存在**，否则编译错误：
  `error: #[no_std] module must define 'fn main()'`。

### freestanding 不切换链接方式

> ⚠️ **两个 freestanding 目标只切换「调用约定归属 + 入口钩子」，不切换链接方式。**
>
> **链接行是按源文件里有没有 `#[no_std]` 分支的，跟 `--target` 无关。**

| 源文件里有 `#[no_std]` 吗 | 链接行 |
|---|---|
| **没有** | 链 `runtime.o` + `helpers.o`（C 运行时 bridge）+ Windows 系统库 + `-lm` |
| **有** | **不链**上面两个，改加 `-nostartfiles -nodefaultlibs -Wl,--entry=main -lgcc` |

也就是说：`--target=amd64_win_freestanding` 本身**不会**让你不链 C 运行时。
要得到纯 freestanding 产物，**源文件里还得写 `#[no_std]`**。

两条分支都带 `-g0 -Wl,--build-id=none -Wl,--stack,67108864 … -lm -lkernel32 -luser32 -lshell32 -ladvapi32`
—— **Windows 系统库与 `-lm` 是无条件加的**（`#[no_std]` 也加）。
真正的 UEFI / 裸机镜像需要自行用 lld-link（`/SUBSYSTEM:EFI_APPLICATION /ENTRY:efi_main`）
或自定义链接行完成。

### 目标 → ABI → 链接方式

| 目标 | ABI（调用约定） | 入口符号 | 链接方式 |
|---|---|---|---|
| `amd64_win` | MS x64 | `main_jhyy` | hosted：链 C 运行时 + Windows 系统库 |
| `amd64_sysv` | SysV AMD64 | `main_jhyy` | hosted（同上；跨目标必须 `--no-link`） |
| `amd64_win_freestanding` | MS x64（与 `amd64_win` 逐字节相同） | 用户自备（`efi_main` / `_start`） | **取决于源文件有没有 `#[no_std]`**，不是取决于 `--target` |
| `amd64_sysv_freestanding` | SysV AMD64（与 `amd64_sysv` 逐字节相同） | 用户自备（`efi_main` / `_start`） | 同上 |

> ⚠️ **输出容器格式不由 `--target` 决定**，而由宿主工具链的 `ld` 决定
> （`link_with_gcc` 没有 target 参数）。各目标的 PE / ELF 产出只是**惯例**（ABI § 12.9）。
>
> 推论：**除 `amd64_win` 外的目标都只能 `--no-link`**，拿 `.s` 去用与目标匹配的工具链链接。

---

## FFI

| 方向 | 支持的参数 / 返回类型 |
|---|---|
| JHYY → C | 全部基础类型、`*T`、`bool` |
| C → JHYY | 同上 |

- `extern fn` 只声明、不生成函数体，链接期由 `ld` 解析符号。
- **不支持**：struct / enum 按值跨 FFI 边界、变参函数（JHYY 侧需逐参数列出）、回调函数。
- ⚠️ `extern fn` 的参数 / 返回类型**不做编译期限制**——声明 struct 参数能编译通过，
  但实际按地址传，与 C ABI 不符（静默不符，无报错）。
- 字符串字面量是 UTF-8 字节序列，存放在 **`.data`** 段，以 NUL 结尾，作为 `*u8` 传给 C，
  兼容 C 的 `char*`。

---

## 已知偏离与未实装项

ABI § 12 是**有意记录、有门或已登记**的事实，不是遗漏。

> § 12 的表**只列当前仍未闭合的项**——已修复的偏离会从表里移除，**编号随之前移**
> ⇒ 引用时请以条目内容而非编号为准。摘要：

| # | 项 | 性质 |
|---|---|---|
| 12.1 | **struct / enum 返回值在所有目标无条件走 sret**，无大小阈值——SysV 标准应把 ≤16 字节聚合类型放进 `RAX:RDX` / `XMM0:XMM1` | 偏离 SysV |
| 12.2 | **`alignof(enum)` 硬编码返回 4**，与 enum 布局计算用的 `max(4, max_payload_align)` 不一致 | 内部不一致 |
| 12.3 | SysV 的非 struct 标量参数仍借 Win 分类器决定 IR 字母——当前不出错，但是隐式依赖 | 隐患 |
| 12.4 | **SysV 下 MEMORY class 参数与寄存器溢出参数混排 → 编译期报错**；部分合法 SysV 用法当前无法编译 | 能力边界 |
| 12.5 | sret 槽大小 `max(4, sizeof(T))` 与 enum 拷贝按 `total_size` 写入——理论边界，实测恒等 | 理论边界 |
| 12.6 | **栈槽只保证 8 字节对齐**；当前无 16 字节对齐类型，未触发 | 能力边界 |
| 12.7 | **全 spill，只保存 `RBP`**，栈帧显著偏大，依赖 64 MB 栈预留补偿 | 实现特征 |
| **12.8** | **UEFI EFIAPI wrapper 未实装**：freestanding 的两个钩子（`emit_entry_point` / `no_crt_init`）**都是空实现**——编译器不生成 EFIAPI wrapper，也不自动抑制 CRT / runtime 链接。entry 符号由用户自行提供 | **未实装** |
| 12.9 | **无交叉编译容器后端**：`--target` 不切换 PE / ELF 产出 | 能力边界 |
| 12.10 | **无 aarch64 / riscv64**；`.jhyynb` 原生二进制格式仍是设计稿，未实装 | 未实装 |
| 12.11 | SysV eightbyte 宽度规则**只对第 0 个 eightbyte 成立**——第 1 个及以后恒为 8 字节 | 偏离 SysV |
| 12.12 | SysV 溢出的 `f64` 栈参缺 16 字节对齐 | 偏离 SysV |
| 12.14 | **Windows 控制台 UTF-8 由运行时设置**：`runtime.c` 的 `main` 在 **stdout 是控制台时**调 `SetConsoleOutputCP(CP_UTF8)` + `SetConsoleCP(CP_UTF8)`；管道 / 重定向时不动代码页 | 实现特征 |

> § 12.14 是这一组里唯一**用户能直接看见**的一条：默认 OEM 代码页在中文 Windows 上是
> CP936 / GBK，程序 `printf` 出去的 UTF-8 字节会被按 GBK 解释 ⇒ 屏幕全是乱码。
> 运行时只在 stdout 是控制台时才切代码页，正是为了避开这个坑。

> **§ 12.8 是当前最大的缺口**：freestanding 目标标着 beta 不是因为约定没定，
> 而是因为**入口路径还没接上**。用户得自己提供 `efi_main` 或 `_start`。

---

## 稳定性承诺

ABI § 9 明确分成两栏：

| 此版本**锁定**（不因 minor / patch 改变） | **可能**在后续版本改变 |
|---|---|
| 基础类型的 sizeof / alignof | struct / enum 返回值在 SysV 上的 sret 处理 |
| 指针宽度（64 位） | `alignof(enum)` 的取值 |
| struct 字段对齐与排列算法 | 名称修饰方案（引入类型编码 / 重载编码） |
| enum 的 tag（`i32`，offset 0）布局 | SysV 分类器对非 struct 标量的处理 |
| 四个目标的调用约定归属（哪个目标用哪套约定） | 栈槽对齐粒度 |
| 名称修饰方案的基本形状（`<mod>__<name>` / `<Base>$<T>`） | |

---

## 原文

- ABI v{{abi_version}}（锁定）——
  [`docs/abis/jhyy-abi-v4.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-abi-v4.0.0.md)
- 配套语言规范 v{{spec_version}}（锁定）——
  [`docs/abis/jhyy-lang-spec-v4.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md)
- 已知限制台账——
  [`docs/internal/workarounds.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/workarounds.md)
- 二进制格式（设计稿，未实装）——
  [`docs/abis/jhyy-binary-format-v1.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-binary-format-v1.0.0.md)
