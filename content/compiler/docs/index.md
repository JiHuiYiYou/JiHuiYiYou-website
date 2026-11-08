---
title: 文档首页
description: JHYY 文档首页 —— 从这里开始
layout: docs
project: compiler
zone: docs
---

# JHYY（机会翼游）— Wiki

**一门自举的、静态类型、面向表达式的系统编程语言。**

这个 wiki 是仓库 README 的长文版：指南、导览，以及那些反复被问到的问题的答案。
README 是地图，这里是走一遍。

> **这里没有任何东西是真相源——仓库才是。**
> 数字、排期、已知限制都会变；这个 wiki 只是**一份「真相在哪」的指南**。
> 每一页都指向真正拥有那个事实的文档。
> 如果 wiki 页面和仓库文档冲突，**以文档为准**——请提个 issue，我们来把页面改对。

---

## 从这里开始

| 你想…… | 去这里 |
|---|---|
| 装好编译器，跑第一个程序 | [[快速上手]] |
| 学这门语言 | [[语言导览]] |
| 从源码构建编译器、跑测试 | [[构建与测试]] |
| 搞清楚编译器是怎么搭起来的 | [[架构]] |
| 找一个反复出现的问题的答案 | [[常见问题]] |
| 贡献一个修复或一个功能 | [CONTRIBUTING.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/CONTRIBUTING.md) |
| 报告安全问题 | [SECURITY.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/SECURITY.md) |

---

## 一段话讲清这个项目

JHYY 是一门**用自己写的**系统编程语言。`compiler/src0/*.jhyy` 是编译器唯一的实现
——树里没有 bootstrap 的 C 编译器，也没有 vendored 进来的后端。编译器先编译自己，
再让编译出来的自己编译自己，而门要求这两代之间产出的汇编**逐字节相同**。
不动点是**跑出来的**，不是假设出来的。

后端是**自己写的 amd64 代码生成器**。Windows 上产出 PE/COFF，Linux 上产出 ELF。
没有 LLVM，没有 QBE，没有垃圾回收，也没有托管运行时；随附的运行时只有一个很小的
C 支撑库。

想看完整版，读 [README](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/README.md)
（中文版是 [README.zh-CN.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/README.zh-CN.md)）。

---

## 三件不一样的事

1. **自举是被验证过的。** 不是「编译器能编译自己」，而是「第二代与第一代逐字节相同」
   ——每次构建都查，结果随每次发布一起公开。
2. **没有 vendored 后端。** amd64 代码生成器是 JHYY 自己写的代码。它消费的中间表示
   也是 JHYY 自己的格式：借了 QBE 的**语法**做起点，但没有任何 QBE 代码被 vendored、
   被链接或被执行。
3. **没有 GC，没有托管运行时。** 显式指针、可预期的类 C ABI，以及面向 freestanding
   目标的 `no_std` 模式。

---

## 真相在哪

| 问题 | 文档 |
|---|---|
| 当前版本、回归基线、排期 | [`docs/internal/FACTS.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md) —— 所有会变的数字的单一真相源 |
| 怎么写 `.jhyy` | [语言规范](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md)（已锁定） |
| FFI、struct 布局、调用约定 | [ABI 白皮书](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-abi-v4.0.0.md)（已锁定） |
| 已知的编译器缺陷与绕法 | [workaround 台账](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/workarounds.md) |
| 编译器是怎么搭起来的 | [架构速览](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/architecture.md) |
| 怎么构建、测试、发版 | [构建与运行](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/build.md) |
| 每个版本改了什么 | [CHANGELOG.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/CHANGELOG.md) |
| 按版本格排的当前计划 | [`docs/plans/v4/`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/tree/main/docs/plans/v4) |

---

## 这个 wiki 怎么维护

wiki 是**手写的伴生文档**，不是生成出来的产物——它的讲解顺序和仓库不一样，也允许
更口语一些。三条规矩让它保持诚实：

1. **不复述数字。** 一个把版本、数量或体积抄下来的 wiki 页面，写完第二天就是错的。
   页面改为指向拥有那个数字的文档。
2. **不复述台账。** 已知限制住在语言规范的附录 B 和公开的 workaround 台账里，
   wiki 只负责指路。
3. **欢迎订正。** 如果某页和仓库冲突，仓库是对的——提个 issue，说明哪一页过时了。
