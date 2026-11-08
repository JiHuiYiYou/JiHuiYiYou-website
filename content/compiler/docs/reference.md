---
title: 参考总览
description: 语言、契约、工具链三类参考的入口与它们各自保证什么
layout: docs
project: compiler
zone: docs
---

# 参考总览

这一页是「语言参考」这一组的索引。JHYY 的参考分三层，每一层保证的东西不一样——
把它们混在一起读，很容易把「这门语言怎么写」和「两个产物之间怎么互认」搞成同一件事。

## 三层参考

| 层 | 回答什么问题 | 它保证什么 | 版本性质 |
|---|---|---|---|
| **语言规范（spec）** | 语法与语义 | 什么是合法程序、每条表达式什么意思、哪些行为被定义 | **锁定的契约** |
| **ABI** | 类型布局、调用约定、链接规则 | 编译器、产物、外部库之间怎么互认 | **锁定的契约** |
| **CLI / 标准库** | 具体工具和 API 怎么用 | 命令怎么敲、函数叫什么、返回什么 | 跟工具链版本走 |

前两层是**契约**：实现必须遵守它们，遵守了才是「JHYY」。第三层是**用法**，
它随着工具链演进，不承诺稳定。

---

## 契约版本 ≠ 工具链版本

这是最容易被绕进去的一件事。

**语言规范 v4.0.0** 和 **ABI v4.0.0** 各自锁在 2026-10-24，随 `v4.0.0 final` 一同锁版。
工具链是另一条独立的线——当前稳定版是 v4.1.4（版本会变，以[下载页](/compiler/download/index.html)为准）。

也就是说：

> **v4.1.x 是对 v4.0.0 契约的实现演进，不是对契约的修改。**

新版本编译器可能多支持一个语法糖、多修一个 bug，但只要规范和 ABI 还是 v4.0.0，
产物的互认规则就一个字没变。反过来，某天规范升到 v5.0.0，那是一份**新的契约**，
旧产物的兼容性需要单独评估。

一个推论：**写代码时该引哪一份，取决于你要互认的是谁。**
和另一个 JHYY 产物互认 → 看 ABI v4.0.0。和 C 库互认 → 同样看 ABI v4.0.0。
只是想知道「怎么写」→ 看规范 v4.0.0。

---

## 四份参考

| 参考 | 讲什么 | 权威原文 |
|---|---|---|
| [语言规范 v4.0.0](/compiler/docs/spec.html) | 语法、类型系统、语义边界 | [`docs/abis/jhyy-lang-spec-v4.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md) |
| [ABI v4.0.0](/compiler/docs/abi.html) | 类型布局、调用约定、链接规则 | [`docs/abis/jhyy-abi-v4.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-abi-v4.0.0.md) |
| [标准库](/compiler/docs/stdlib.html) | 八个模块的真实 API | [`compiler/src0/std/`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/tree/main/compiler/src0/std) |
| [CLI 参考](/compiler/docs/cli.html) | 命令、参数、退出码 | 仓库 `README.md` 的 CLI 段 |

还没读过规范的话，从[语言导览](/compiler/docs/tour.html)起步更快；
要跑通第一个程序，看[快速上手](/compiler/docs/getting-started.html)。

---

## 文档不是真相源，仓库才是

这一页、这一组参考、以及整个官网 wiki，都是**手写的伴生文档**。
它们的作用是告诉你「事实住在哪个文件里」，不是复述事实。

理由很直接：会变的数字（版本号、回归基线、限制条目）抄进第二份文档，
第二天就有两份互相矛盾的数字，而读者不知道该信哪一份。

所以每一条断言都要能回溯到一个文件：

| 事实类型 | 住在哪 |
|---|---|
| 会变的数字、排期 | [`docs/internal/FACTS.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md) |
| 已知限制与绕法 | [`docs/internal/workarounds.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/workarounds.md) |
| 每个版本改了什么 | [`CHANGELOG.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/CHANGELOG.md) |
| 编译器怎么搭的 | [`docs/internal/architecture.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/architecture.md) |

仓库地址：[github.com/JiHuiYiYou/JiHuiYiYou-compiler](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler)

发现 wiki 和仓库对不上——**以仓库为准**，然后提个 issue 让我们把页面改对。

---

## 一份不在这一组里的文档

[`docs/abis/jhyy-binary-format-v1.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-binary-format-v1.0.0.md)
——JHYY 原生二进制格式（`.jhyynb`）的设计稿，**尚未实装**（ABI § 12.10）。
现在没有产物实现过它，所以它不构成任何兼容性承诺。

---

## 接下来

- [语言规范 v4.0.0](/compiler/docs/spec.html) —— 写 JHYY 代码要遵守什么。
- [ABI v4.0.0](/compiler/docs/abi.html) —— 产物之间怎么互认。
- [标准库](/compiler/docs/stdlib.html) —— 八个模块的函数签名与坑。
