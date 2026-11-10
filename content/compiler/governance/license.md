---
title: 许可证
description: MIT 的确切条款，以及各仓库的许可现状
layout: docs
project: compiler
zone: governance
---

# 许可证

四个仓库里三个用 MIT，一个还没有许可证文件。这一页写两件事：MIT 的确切条款是什么，
以及每个仓库实际是什么状态。

---

## MIT 的条款

用的都是 MIT 官方模板，版权行是 `Copyright (c) 2026 JHYY` —— 署名主体是项目名，
不是某个自然人。

### 允许什么

获得软件及文档副本的人，可以**自由地**使用、复制、修改、合并、发布、分发、再授权、
出售这些副本，**不受任何限制**（"without restriction"）。这八个动词就是授权范围，
没有附加条件。

### 要求什么

**唯一的一条要求**：上述版权声明与本许可声明必须包含在软件的所有副本或实质性部分中
（"The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software"）。

也就是说：改代码可以，改文件名可以，闭源分发可以，商用可以 —— 只要那一段版权声明
和许可声明**跟着走**。

### 不保证什么

软件按「原样」提供，**不附带任何明示或默示的担保**，包括但不限于对适销性、
特定用途适用性、不侵权的担保；作者或版权持有者不对任何直接、间接、附带、特殊、
后果性或惩罚性损害承担责任。

### MIT 没有涵盖的

- 不要求声明你做了哪些修改
- 不含明示的专利授权条款
- 不含互操作例外（不像 GPL 那样写明兼容哪些许可证）
- **不授予商标权**（见最后一节）

---

## 四个仓库的许可现状

| 仓库 | 许可证文件 | 版权行 | 状态 |
|---|---|---|---|
| Compiler（`JiHuiYiYou-compiler`） | 根目录 `LICENSE` | Copyright (c) 2026 JHYY | MIT，与官方模板一致 |
| IDE（`JiHuiYiYou-IDE`） | 根目录 `LICENSE` | Copyright (c) 2026 JHYY | MIT，与 Compiler 那份**逐字节相同** |
| OS（`JiHuiYiYou-OS`） | 根目录 `LICENSE` | Copyright (c) 2026 JHYY | MIT，与 Compiler 那份逐字节相同；唯一差别是文件末尾没有换行符 |
| for-VEX（`JiHuiYiYou-for-VEX`） | 根目录 `LICENSE` | Copyright (c) 2026 JHYY | MIT，与 Compiler 那份**逐字节相同**（2026-11-08 补上） |

编译器仓里另有一份 `vscode-ext/LICENSE`，也是同样的 MIT，随扩展一起分发。

四个仓现在**都有** MIT 许可文件（for-VEX 那份是 2026-11-08 补上的，与 Compiler
逐字节相同）；OS 那份只差一个末尾换行符。

---

## 依赖与第三方代码

MIT 只覆盖 JHYY 自己写的代码。仓库里自有的部分很干净：

| 组件 | 是什么 | 许可 |
|---|---|---|
| `compiler/src0/*.jhyy` | 编译器唯一实现 | MIT（明确） |
| `compiler/runtime/runtime.c` / `runtime.h` | C 支撑运行时 —— 用户程序链接时用的那一份（hosted 模式的 `main → main_jhyy` 桥） | MIT（明确） |
| `compiler/src0/jhyy_helpers.c` | 编译器与 libc 之间的 C 桥 | MIT（明确） |
| `compiler/runtime/no_std_core/*.jhyy` | `#[no_std]` 时的替代实现（memcpy / memset / panic_handler / `__start_kernel`）—— **是 JHYY 写的，不是抄来的 C 库** | MIT（明确） |

这四份代码里没有第三方版权头，也没有从别处搬运的实现。

### 真正要清点的是随包分发的东西

安装器随包发两样外部代码，两样的处理方式不同：

| 组件 | 用途 | 是否随产物分发 | 许可状况 |
|---|---|---|---|
| MSYS2 ucrt64 工具链（gcc / binutils / CRT / 头文件） | 汇编与链接；让装机用户不需要 MSYS2 | 是 | **已成文**：工具链目录下有 `SOURCES.txt`，逐个列出 MSYS2 包、SPDX 许可标识与源码 tarball URL，另有 `LICENSES/<包名>/` 放着许可证正文；文件末尾写明「对应源码怎么取」 |
| .NET 8 Desktop Runtime | 安装器里的 `jhyy-setuc`（写 UserChoice）需要 | 是 —— 安装器把官方 dotnetcli 镜像上的 `dotnet-runtime-8.0.30-win-x64.exe` 一起打进去，版本与 sha256 都钉在 `installer/build.ps1` 里 | .NET 运行时本身是 MIT；它自己再捆绑的组件（ICU 等）另按微软的分发条款走。**安装器的清单里没有单独列出这一项** ⇒ 需要补 |

构建期依赖（MSYS2 / GCC / binutils / WiX / Node.js / Electron）本身不随产物分发，
只在开发机上用；但**只要有一样被复制进了安装包，就进入再分发范围**，得跟上清单。

### 需要逐项清点的

- IDE 与 VS Code 扩展的 Node.js / Electron 依赖树 —— `node_modules` 里有上百个包，
  各自一套许可，**目前没有成文的清单**
- for-VEX 路线 B 要链 VEX 官方 SDK（`libv5rt.a` / `stdlib_0.lib` / `lscript.ld`），
  那是 VEX Robotics 的东西，**再分发条件未知**
- OS 仓将来出的内核镜像，若内嵌第三方代码，需要同样的清单

⇒ 补法可以直接照抄工具链那份 `SOURCES.txt` 的体例：一个包一行，许可 + 源码出处。

---

## 商标

**仓库里没有成文的商标政策。** 没有 `TRADEMARK.md`，没有任何文件说明 logo 或
「机会翼游 / JHYY」这两个字样的使用边界。

logo 与书法字样的实际位置：`vscode-ext/icon.png` / `icon.svg` / `icon-animated.svg` /
`jhyy-calligraphy.png`、`installer/assets/icons/`、IDE 仓的 `assets/`。

MIT 本身**不授予商标权** —— 它授权的是版权与使用许可，不涉及商号。所以在没有成文
政策之前，按以下边界走（MIT 的通行做法）：

| 可以 | 不可以 |
|---|---|
| 在描述性用途里用 logo 与「机会翼游 / JHYY」字样（说明「这是给 JHYY 写的工具」「这是 JHYY 的编译器」） | 暗示得到官方背书、授权或认证 |
| 在发行物里原样使用 | 改 logo（改比例、配色、加效果） |
| 用「基于 JHYY」「for JHYY」这类描述 | 用「JHYY」注册商标或域名 |

**打算怎么补**：写一份 `TRADEMARK.md`，把上面这张表固化成正式条款，并指明谁负责
维护它 —— 一条没有责任人的商标政策比没有更糟。

---

## 相关

- [治理总览](/compiler/governance/index.html)——决策方式与发布节奏
- [仓库地图](/compiler/governance/repo-map.html)——四个仓库各管什么
