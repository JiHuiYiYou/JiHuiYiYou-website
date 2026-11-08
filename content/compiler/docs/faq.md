---
title: 常见问题
description: 反复被问到的问题与它们的答案
layout: docs
project: compiler
zone: docs
---

# 常见问题

反复被问到的问题，以及当下为真的答案。答案变了就是仓库说了算——见
[语言规范](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md)
和 [FACTS.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md)
里的权威版本。

---

## 用编译器

### 能在 Linux 或 macOS 上跑编译器吗？

不能直接跑。**编译器是个 Windows 程序**——`jhyy.exe` 是 PE 可执行文件，宿主必须是
Windows（或 Wine）。这是刻意的设计决定，不是疏漏。

**可移植的是产出**：SysV 目标产出 Linux ELF 汇编，CI 会在 Linux 上链接并运行它。
所以「JHYY 程序能在 Linux 上跑」成立，「JHYY 编译器能在 Linux 上跑」目前不成立。

### 怎么查版本？

**`jhyy --help` 的第一行**就是版本横幅。没有 `jhyy --version` 这个选项——它从来没
存在过，这么写会打印 `jhyy: unknown option --version` 然后以 1 退出。

### 为什么入口是 `main_jhyy` 而不是 `main`？

因为托管入口的签名不一样：`main_jhyy(argc: i32, argv: *u8) -> i32`，其中
`argc` / `argv` 可省略。C 运行时的 `main` 负责桥接。在 freestanding 的 Linux 运行时
上是同一个约定——`crt0.S` 调 `main_jhyy`，并以它的返回值退出。

### 为什么 `jhyy compile a.jhyy b.jhyy` 把 `b.jhyy` 忽略了？

因为编译器**只接受一个输入文件**，多余的 `.jhyy` 参数被静默忽略——不报错、不警告。
要编译多个文件就用 `import`：在 `main.jhyy` 里写 `import lib;`，编译器会顺着导入
图把 `lib.jhyy` 一起拉进来。

### 为什么我的退出码看起来不对？

如果是用 MSYS2 bash 读 `$?` 取的，它被截成了 8 位（`值 & 0xFF`）。请改用 harness 或
Python `subprocess` 取退出码。期望值 827 读回来是 59，501 是 245，300 是 44，
1000 是 232。

### 为什么编译器不给我链 Linux 程序？

**这份构建链不了交叉目标**——自带的链接器永远产出 Windows `.exe`。加 `--no-link`，
自己用匹配的工具链链 `.s`；三步流程见 [[构建与测试]]。

### 用 JHYY 需要 MSYS2 吗？

不需要。安装器自带一份最小原生工具链，终端用户只要有 Windows 就行。只有**从源码
构建编译器**才需要 MSYS2。

---

## 语言

### 有垃圾回收吗？有分配器吗？有 RAII 吗？

**没有 GC，没有自动所有权，没有 RAII。** 内存是显式的：裸指针、手动分配，以及——
如果你想要——标准库里的 arena 分配器，加上 `defer` 做作用域退出清理。`defer` 按
LIFO 在作用域退出时执行，但**隐式尾返回时不执行**。

### 为什么没有 `std::` 前缀？

因为 `import` 直接接模块名：`import vec;`，而不是 `import std::vec;`。写带前缀的
形式是编译错误。

### 能调 C 库吗？

能——`extern fn` 按 C ABI 调 C 函数。两个提醒：**没有可变参数形式**（每个参数都得
一个一个写出来），而且**参数类型不会跟 C 签名对拍**，写错了照样编译通过，运行时
才出问题。

### 能写捕获变量的闭包吗？

还不能——今天捕获是**编译错误**。块表达式闭包是有的，只是不能捕获。

### 泛型和 trait 有了吗？

泛型有一部分；**trait 还没实现**。两者都在公开的路线图上——当前排期见
[FACTS.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md)。

### 浮点数呢？

`f32` 和 `f64` 作为类型存在，但标准库**还没有浮点格式化器**——所以今天没法打印浮点数。

### JHYY 能上生产吗？

**还不行。** 项目是 pre-1.0：自举闭环能跑，回归套件是绿的，但语言规范还在动，
不承诺版本之间的语义稳定性。哪些能用、哪些不能，README 的状态表里有一张表。

---

## 项目

### 中间表示既然是「QBE 风格」，那为什么没有 QBE？

因为借的是 QBE 的**语法**，它简洁又可读。QBE 本身已经从项目里移除：amd64 后端是
JHYY 自己写的代码，IL 文本也是 JHYY 自己的格式。没有任何 QBE 代码被 vendored、
被链接或被执行。

### 「编译器把自己编译得逐字节相同」是不是就说明编译器是对的？

**不是。** 它说明编译器**精确地复现自己**——这是关于生成确定性的陈述。一个确定性的
错误编译器也能完美闭环。这就是经典的 "trusting trust" 缺口，由另一道门覆盖：
回归套件。

### 为什么仓库公开维护一份已知缺陷台账？

因为一个偷偷绕开自身缺陷的编译器，比一个公开承认缺陷的编译器更糟。台账
（[workarounds.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/workarounds.md)）
是公开维护的：每一条都写清楚问题是什么、什么时候触发、怎么绕、什么能取代这个绕法。
条目只关闭、不删除——它是一条审计轨迹。

### 怎么报 bug？

带上**最小复现**、期望输出与实际输出、版本、退出码。细节见
[贡献指南](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/CONTRIBUTING.md)，
issue 模板问的就是这几个字段。

### 怎么报安全问题？

**不要开公开 issue。** 请用私有 advisory 表单——流程、范围、响应时间表都在
[SECURITY.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/SECURITY.md)里。

### 路线图在哪？

权威排期在
[FACTS.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md)，
每个版本格一份计划在
[`docs/plans/v4/`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/tree/main/docs/plans/v4)。
预留版本号上的数字是占位——每份计划都自带一份「启动时复核清单」，领用那一格时按
当时的实际情况重新核对。

---

## 还是卡住了？

- [Discussions](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/discussions) —— 提问与设计讨论。
- [Issues](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/issues) —— bug 与功能请求。
- [[首页]] —— 回到起点。
