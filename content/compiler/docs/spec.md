---
title: 语言规范 v4.0.0
description: 锁定的语言契约：语法、类型系统、语义边界
layout: docs
project: compiler
zone: docs
---

# 语言规范 v4.0.0

**规范全文在仓库里，不在这里。**
原文：[`docs/abis/jhyy-lang-spec-v4.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md)

本页是那份规范的**导读 + 索引 + 关键约定摘要**。规范正文的每一条都对应编译器源码中
可复现的行为；本页每一条也一样。**两者冲突时以仓库原文为准。**

规范锁在 v4.0.0（2026-10-24 随 `v4.0.0 final` 一同锁版）。工具链版本是另一回事，
见[参考总览](/compiler/docs/reference.html)。

---

## 规范覆盖了什么

| 章 | 内容 |
|---|---|
| § 1 | 程序结构：`main_jhyy` 入口、`import` 多文件、注释、顶层声明 |
| § 2 | 类型系统：基础类型、复合类型、别名、推断、字面量、`Cap<T>`、`PhantomData<T>`、`sizeof`/`alignof` |
| § 3 | 变量与绑定：`let` / `let mut`、shadowing、顶层全局变量、复合赋值 |
| § 4 | 运算符：12 级优先级、语义要点、聚合类型相等比较、`as` 转换 |
| § 5 | 控制流：`if`/`else`、`while`、`for`、`break`/`continue`、`return`、`match`、闭包 |
| § 6 | 函数：签名、递归、`defer`、属性 |
| § 7 | 指针与借用：`&x`、指针算术、`&T` / `&mut T` |
| § 8–9 | `struct`、`enum` |
| § 10 | 定长数组与切片 |
| § 11 | 泛型：struct / enum / 函数、turbofish、调用点推断 |
| § 12 | 顶层 `const` 数组 |
| § 13 | 模块与导入 |
| § 14 | FFI（`extern fn`） |
| § 15 | 标准库（8 个模块） |
| § 16 | 命令行 |
| § 17 | 底层与 OS 扩展：`volatile`、`asm!`、`#[naked]`、`#[link_section]`、`#[no_std]`、内存屏障、freestanding |
| § 18 | 错误码与诊断 |
| § 19–20 | Debug ABI 与 wire format（跨项目契约） |
| 附录 A–D | 与 v1.3.0 的差异、未实装清单、自举兼容性、完整示例 |

---

## 关键约定

下表是**写代码时最容易记错的那批**。完整表述在规范原文对应章节。

### 类型系统

| 约定 | 内容 |
|---|---|
| 基础类型 | `i8 i16 i32 i64 u8 u16 u32 u64 f32 f64 bool`，外加零大小类型 `()` |
| 没有 `char` | 字符字面量的类型是 `i32`，值是 Unicode codepoint（全码点 U+0000–U+10FFFF） |
| `()` | 是 ZST（sizeof 0 / alignof 1），但**类型位置不认它**：`let x: () = ();` 是解析错误 |
| 复合类型 | `*T` / `[T; N]` / `[*]T` / `struct` / `enum` / `&T` / `&mut T` / `Cap<T>` / `PhantomData<T>` / `volatile T` |
| `fn(...)` 类型 | **类型位置不认这个语法** ⇒ 闭包值无法当函数值传递 |
| 名义类型 | `struct` / `enum` 按**声明名**比较，不是按布局——布局相同、名字不同就是不同类型 |
| 类型别名 | 透明：`type Age = i32` 与 `i32` 完全等价 |
| 推断 | 参数**必须**显式标注类型；局部变量从初始化表达式推断 |
| 默认字面量类型 | 无后缀整数 → `i32`；无后缀浮点 → `f64` |
| 隐式转换 | 整数 ↔ 浮点**不允许**，必须 `as` |

### 字面量

| 约定 | 内容 |
|---|---|
| 整数进制 | 十进制 / `0x` / `0X` / `0o` / `0O` / `0b` / `0B`；**前导零按八进制**（`077` = 63） |
| 下划线分隔 | `1_000_000` **不支持**（解析错误） |
| 整数后缀 | `i8 i16 i32 i64 u8 u16 u32 u64` |
| 整数取值范围 | 按 `u64` 精确求值；越界**编译报错**（`integer literal out of range`），**不静默饱和** |
| 浮点形式 | 只支持 `N.M`（可带后缀）——**指数写法 `1.0e10` 解析失败** |
| 浮点后缀 | `f32` / `f64` / `f`（`f` = `f64`） |
| 字符串 | 类型是 `*u8`（NUL 结尾的 UTF-8 字节串），落 **`.data` 段**；**没有隐式 decay** 到 `[*]u8` |
| 布尔 | `true` / `false`；编译器**不做 0/1 归一化**——非字面量来源的 `bool` 可能是任意字节 |

### 函数与过程

| 约定 | 内容 |
|---|---|
| 返回值 | 函数体**最后一个表达式**即返回值，不需要 `return` |
| 参数 | 必须显式标注类型；**不支持**默认参数与变参 |
| 嵌套 | **不支持嵌套函数**——所有函数必须在顶层声明 |
| `defer` | 在**显式 `return`** 路径上按 LIFO 执行；⚠️ **函数体末表达式的隐式返回不触发 defer** |
| `#[inline]` | 只在**函数体是单条 `return <expr>;`** 时真正展开；多语句 / if-else / 循环 / 递归都回退成普通 `call` |

### 模块与导入

| 约定 | 内容 |
|---|---|
| 语法 | 单个标识符：`import mylib;`——**不带 `std::` 前缀**（`import std::vec;` 是解析错误） |
| 查找顺序 | main 文件旁边 → 标准库目录（两级回落） |
| 传递性 | 递归：`main → a → b` 时 `main` 能用 `b` 的声明 |
| 循环 | 成环报 `circular import '...'`，不崩溃 |
| 命名空间 | 不同模块可定义同名函数，用 `mod::fn()` 限定调用 |
| 多文件 | 组合靠 `import`，**不靠命令行**——命令行只接受一个输入文件，多余的 `.jhyy` 参数被**静默忽略** |

### enum 与 match

| 约定 | 内容 |
|---|---|
| enum 布局 | tag 是 `i32`，offset 0，从 0 起按声明顺序递增 |
| payload | **一个变体最多带一个 payload**（`Rect(i32, i32)` 是解析错误）——要装多个字段就把 payload 换成 struct |
| match 模式 | 字面量 / `_` / 多值 `pat1 \| pat2` / 范围 / 枚举绑定 |
| 范围语义 | ⚠️ **match 里的 `0..10` 是闭区间（含两端）**，而 `for i in 0..10` 是半开区间 |
| arm body | 只能是**单个表达式**——不能写 `return`，也不能写成语句块 |
| arm 作用域 | 每个 arm 独立，模式绑定**遮住**外层同名变量，arm 结束后不外泄 |
| 穷尽性 | 已实装：enum 上每个变体必须被覆盖或由 `_` 兜底，否则报 `non-exhaustive match: missing variant` |
| 不支持 | **guard pattern**（`Some(x) if x > 0`）；**二层以上的嵌套 pattern**（编译期拒绝） |

### 指针与借用

| 约定 | 内容 |
|---|---|
| 指针宽度 | 8 字节；空指针是整数 0；算术步长是 `sizeof(T)` |
| `&x` | 类型是 `*i32`；⚠️ 编译器**不检查** `x` 是否可变——不可变绑定也能取地址 |
| 指针差 | `p - q` 的结果是**元素个数**（`i64`），不是字节差 |
| 成员访问 | ⚠️ **`->` 不是成员访问运算符**——通过指针访问字段写 `(*p).field` |
| `&T` / `&mut T` | 都是 8 字节单指针；`is_mut` 是编译期标记，不占内存 |
| 不支持 | 链式 `&&T`；生命周期标注 `'a`；reborrow |
| 借用检查 | 只做到最小程度——同一作用域内重复 `&mut` 同一变量被拒绝；完整 NLL / Polonius **未实装** |

### FFI（`extern fn`）

| 约定 | 内容 |
|---|---|
| 语义 | 只声明、不生成函数体；链接期由 `ld` 解析符号 |
| 符号 | 汇编符号**不加修饰** |
| 变参 | **不支持**——`printf` 的每个参数必须在 JHYY 侧逐个列出 |
| 回调 | **不支持** |
| struct / enum 按值 | **不支持**跨 FFI 边界 |
| ⚠️ 类型不检查 | `extern fn` 的参数 / 返回类型**不做编译期限制**——声明 struct 参数能编译通过，但实际按地址传，与 C ABI 不符（静默不符，无报错） |

### 属性

| 属性 | 作用 |
|---|---|
| `#[inline]` | 提示内联（见上） |
| `#[naked]` | 无 prologue / epilogue；函数体**只能**含 `asm!(...)`；不参与 sret；被调用方需自行保存 callee-saved 寄存器 |
| `#[link_section("...")]` | 只改符号落入的 section，**不改变调用约定**；section 名必须是可打印 ASCII |
| `#[no_std]` | **模块级**属性；不链接 C 运行时启动文件，入口符号改为 `main`；没有 `fn main` 会报 `error: #[no_std] module must define 'fn main()'` |

### 内联汇编与内存屏障

| 约定 | 内容 |
|---|---|
| `asm!("...")` | 单字符串字面量；**不支持**操作数约束、模板占位符、clobber 声明；AT&T 语法，x86-64 only |
| 落点 | **内联在函数体当前位置**（hex 编码进 IL 的 `dbgasm` 通道，后端在原位解回写入 `.s`）——早期实现把它 append 到 `.s` 末尾，成为死字节 |
| 表达式位置 | 语法上可用，但**返回值语义未定义** ⇒ 惯例写在语句位置 |
| `volatile T` | 只修饰**基础类型**；布局与 `T` 完全一致；保证单线程内每次 load 命中内存、每次 store 写回、不重排 |
| `fence_*` | `fence_seq_cst()` / `fence_acquire()` / `fence_release()` → `mfence` / `lfence` / `sfence`；内联在调用点；**只覆盖 x86-64** |
| 跨线程 | `volatile` **不提供**跨线程顺序保证——那要靠 `fence_*` |

### 其他容易踩的

| 约定 | 内容 |
|---|---|
| 顶层 `let mut` | 是**运行时全局变量**，但初始化器**必须是整数常量表达式**；非整数类型的初始化器被丢弃（读到 0 或垃圾） |
| 顶层 `const` | 只支持**顶层** `const` 数组；元素位置放函数调用能编译通过，但不会被求值（运行时取到 0） |
| `sizeof` / `alignof` | 接受**类型**（不是表达式），返回 `i64`；`alignof(enum)` 恒为 4 |
| `type X = ...` | 结尾**不带分号**（带 `;` 报 `unexpected token ';' in expression`） |
| 聚合相等 | `struct` / `enum` / 数组 / 切片按**值**比较；切片只比**头**（指针 + 长度），不逐元素 |
| 聚合大小比较 | `a < b` 这类对聚合类型**编译期报错** |
| 溢出 | 有符号整数溢出是**定义行为**（二进制补码环绕），无运行时检查 |

---

## 预 1.0 的边界

规范自己划了两条线：**正文**只写已实装的行为，**附录 B** 收所有留白。

### 明确留白（未实装）

| 领域 | 留白 |
|---|---|
| 类型 | `()` 在类型位置；`fn(...)` 函数指针类型语法（⇒ 闭包不能当函数值传递） |
| 借用 | 完整 NLL / Polonius 借用检查、生命周期标注 `'a`、reborrow、跨函数借用 |
| 闭包 | 捕获外层变量——**编译期明确报错**，不静默生成错误代码 |
| 表达式 | 块表达式（`let v = { ... };`）；match arm 的 body 是语句块 |
| 泛型 | 约束 `<T: Ord>`、生命周期泛型、const generic、trait objects、HKT |
| FFI | 变参函数、回调函数、struct / enum 按值跨 FFI 边界 |
| `Cap<T>` | 字段访问（`.cnode_idx` / `.depth` / `.rights`）；`T` 本身**不被解析** |
| 标准库 | `std::math` 的 f32 版本与 `tan` / `log` / `exp` / `floor` / `ceil` |
| 其他 | async / await、`std::map`、aarch64 / riscv64、`.jhyynb` 原生二进制格式、`asm!` 的操作数约束与 Intel 语法、match 的 guard pattern、浮点指数写法 |

### 已实装但受限（容易误判成 bug）

| 项 | 现象 |
|---|---|
| `argv` 的类型 | 写成 `*u8`，实际是 `char **` ⇒ `*argv` 只 load 1 字节；读 `argv[i]` 必须先 `argv as **u8` |
| 聚合 `==` 的操作数 | 不接受**函数调用结果**（`make_p(1) == make_p(2)` 编译期报错）；先 `let a = ...;` 存进变量就安全 |
| struct 字面量省略的字段 | **未初始化**（栈上的垃圾），**不是 0**；编译器也不报「缺字段」 |
| struct 字面量字段值类型 | 必须**精确匹配**字段类型——`u8` 字段写 `7`（推断成 `i32`）报 `field type mismatch` |
| 不可变性的写保护 | 未实装——`&x` 对不可变绑定合法，`*p = v` 不报错也**不生效** |
| 函数实参类型 | **不检查**——把 `i32` 传给 struct 形参能编译通过，运行时按 struct 布局读寄存器 → 访问违例崩溃 |
| 顶层全局变量 | 只有**整数类型**的初始化正确求值；`f64` 读到 0，指针 / struct 读到垃圾 |
| `const` 元素 | 不做 const 检查——元素位置放函数调用不会被求值，运行时取到 0 |
| `match` 范围 | 闭区间（与 `for` 相反） |
| `defer` | 不覆盖隐式返回路径 |
| 嵌套 pattern | 二层以上**不支持**（编译期拒绝）；外层 tag 比较与内层 payload 提取都未实装 |

完整的逐条清单在规范**附录 B**，带台账编号的条目在
[`docs/internal/workarounds.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/workarounds.md)。

---

## 规范改动怎么走

规范是**锁定的契约**——不是随手改的文档。

- 任何改动走 [RFC 流程](/compiler/governance/index.html#rfc)，不直接改 `docs/abis/`。
- 锁版不是打个标签就完事：规范正文里的每一条「已实装」都要在
  `compiler/src0/*.jhyy` 里找到对应实现——**自举编译器本身就是规范的最大消费者**。
- `docs/abis/*` 变更后要跑一遍回归（规范改动可能影响 JHYY 端的解析）。

---

## 原文

- 语言规范 v4.0.0（锁定）——
  [`docs/abis/jhyy-lang-spec-v4.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md)
- 配套 ABI v4.0.0（锁定）——
  [`docs/abis/jhyy-abi-v4.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-abi-v4.0.0.md)
- 已归档的旧版（v1.3.0 及其 17 份 v3.x supplement）只在 git 历史里：
  `git show <sha>:docs/abis/<name>`
