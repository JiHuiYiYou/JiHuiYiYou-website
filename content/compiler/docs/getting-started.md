---
title: 快速上手
description: 5 分钟装好编译器并跑出第一个程序
layout: docs
project: compiler
zone: docs
---

# 快速上手

下面全部用的是**发布版**编译器。想自己构建编译器，见 [[构建与测试]]。

---

## 1. 安装

**编译器跑在 Windows x64 上。** 宿主必须是 Windows（或 Wine）——这是设计决定，不是
缺陷。但**产出**不限于 Windows：SysV 目标产出的是 Linux ELF。

去 [GitHub Releases](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/releases/latest)
拿最新版本：

| 产物 | 是什么 |
|---|---|
| `jhyy-installer-*.exe` | GUI 安装器 —— 编译器、`.jhyy` 文件关联、VS Code 扩展、PATH |
| `jhyy-compiler-*.msi` | 同样的内容，不要 GUI —— 给企业 / SCCM 分发用 |
| `jhyy-lang-*.vsix` | 单独的 VS Code 扩展 |

> **使用编译器不需要 MSYS2。** 工具链自带之后，安装器里带了一份最小原生 ucrt64
> 工具链。只有想**从源码构建编译器**时才需要 MSYS2。

每个产物旁边都有 `SHA256.txt` 校验和。

---

## 2. 确认装好了

```bash
jhyy --help
```

**输出的第一行就是版本横幅** —— 这是你确认自己手上是哪个编译器的办法。

> [!NOTE]
> **没有 `jhyy --version` 这个选项。** 它从来没存在过。这么写会打印
> `jhyy: unknown option --version`（外加一句 `try jhyy --help` 提示），然后以 1 退出。

---

## 3. 第一个程序

```jhyy
// hello.jhyy
extern fn puts(s: *u8) -> i32;

fn main_jhyy() -> i32 {
    puts("Hello, world!");
    0
}
```

```bash
jhyy run hello.jhyy
# => Hello, world!
```

> [!IMPORTANT]
> **入口是 `main_jhyy`，不是 `main`。** 托管程序必须定义 `main_jhyy`；它的真实签名
> 是 `main_jhyy(argc: i32, argv: *u8) -> i32`，`argc` / `argv` 可以省略。
> C 运行时的 `main` 负责桥接。

---

## 4. 命令行

下面是 `jhyy --help` 的**原样输出**（编译器打印的帮助是英文的，只有这一份）：

```text
jhyy compiler v{{site_version}} (self-hosted)

usage: jhyy [--target=<triple>] [--no-link] <command> [args]

commands:
  compile <file.jhyy> [-o output]   compile + link -> .exe (a lib without main is compiled only)
  build   <file.jhyy> [-o base]     compile only -> .s (no link; -o is a base name, .s appended)
  run     <file.jhyy>              compile + link + execute
  dump    <file.jhyy>              print the parsed AST tree (parse only; no sema/codegen)

flags:
  --target=<triple>  select target (default amd64_win); see targets below
  --no-link          compile to .s only, skip the link step (required for cross targets)
  --help             show this message and exit

targets:
  amd64_win                x86-64-w64-mingw32 (default; hosted Windows) - the only target this build can link
  amd64_win_freestanding   x86-64-w64-none (UEFI; freestanding, no libc) - .s only (--no-link)
  amd64_sysv               x86-64-linux-none (Linux; SysV ABI) - .s only (--no-link)
  amd64_sysv_freestanding  x86-64-linux-none-freestanding (Linux; no libc) - .s only (--no-link)
```

翻成中文就是：`compile` 编译并链接出 `.exe`（没有 `main` 的库文件只编译不链接），
`build` 只编译出 `.s`（`-o` 是基名，`.s` 后缀自动加），
`run` 编译、链接并执行，`dump` 只解析、打印 AST 树（不跑语义分析也不生成代码）。

> [!NOTE]
> **这是两个不同的「build」。** `jhyy build` 是「把一个 `.jhyy` 编译成汇编」；
> `make all` 是「构建编译器」。两者毫无关系——给任何一个改名都是破坏性变更。

`jhyy dump` 打印的是**解析后的 AST**——一行一个节点，子节点缩进，每行标着
`@file:line:col`。它解析完就停，所以看到的是**语法**，不是编译后的形态。

### 目标三元组

| 三元组 | 产出什么 |
|---|---|
| `amd64_win` | 托管 Windows PE/COFF —— 默认，也是这份构建唯一会链接的目标 |
| `amd64_win_freestanding` | UEFI，无操作系统 |
| `amd64_sysv` | Linux SysV ABI |
| `amd64_sysv_freestanding` | Linux，无 libc |

后三个只产出 `.s`——用与目标匹配的工具链去链接。确切步骤见 [[构建与测试]]。

---

## 5. 新手最容易踩的几个坑

下面每一条在 [[常见问题]] 里都有完整解释。

- **退出码看起来不对。** MSYS2 bash 会把退出码截成 8 位（`值 & 0xFF`）。
  用 harness 或 Python `subprocess` 取退出码，别读 `$?`。
- **只接受一个输入文件。** `jhyy compile main.jhyy lib.jhyy` **只**编译 `main.jhyy`，
  第二个参数被静默忽略。要多文件就用 `import lib;`。
- **交叉目标拒绝链接。** 加上 `--no-link`，`.s` 自己链。
- **没有 `std::` 前缀。** `import std::vec;` 是编译错误——正确写法是 `import vec;`。
- **字符串字面量本身就是 `*u8`。** 不需要转换；`let s: [*]u8 = "x";` 是类型错误。

---

## 6. 接下来

- [[语言导览]] —— 一口气把语言过一遍。
- [[构建与测试]] —— 构建编译器、跑测试、那些门。
- [[架构]] —— 编译器内部是怎么搭的。
- [[常见问题]] —— 高频问题。
- [语言规范](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md)
  —— 权威定义（已锁定；已知限制在其附录 B）。
