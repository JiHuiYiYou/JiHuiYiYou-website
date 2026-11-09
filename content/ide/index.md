---
title: JHYY IDE
description: 拖块编程与文本编辑共享同一棵 AST 的桌面工作台
layout: page
project: ide
zone: ide
---

给 JHYY（机会翼游）做的桌面 IDE：**拖块写、写代码、跟本机的 Claude Code 聊**。
一个 VS Code 式的工作台，两个写代码的视图共享同一棵 AST，诊断永远来自真实的 `jhyy.exe`。

## 三个面板

- **文本视图** —— CodeMirror 6，正常写代码。语法高亮、括号匹配、自动闭合、缩进、补全（关键字、类型、8 个标准库模块），悬停提示能给出**规范章节号**。文件开在标签页里，开第二个不会把第一个顶掉；小黑点按内容算，撤销回上次保存的版本就自动消失。
- **块视图** —— Blockly 13，拖块写程序。工具箱第一屏是「入门」：函数、打印、调用、数字/字符串、变量、返回，另有现成的 **C 函数声明**块（`printf` / `puts` / `malloc` / `free` / `exit`，参数表自动填好）—— 每个 JHYY 程序的第一行不用再靠「原始代码」逃生舱手打。
- **Claude Code** —— 右侧栏里的内嵌对话面板，驱动你机器上**已经装好的 `claude` CLI**（走 stdin 的流式模式，多轮上下文是连着的）。Claude 挂上了 jhyy MCP server，能调 `jhyy_check` 拿**真实编译器**的诊断，而不是靠猜。侧栏还有个「只读」开关，打开后系统提示里会写明「用户要求你不要修改任何文件」。

底部还有一块**默认收起**的面板：点「检查」弹到**问题**页，点「运行」弹到**终端**页。

## 最有说服力的一条：积木和文本共享同一棵 AST

两个写代码的视图是**同一棵树的两个投影**，不是两套代码生成器：

- **改块 → 文本** 实时跟着变（重新生成整份源码并替换文本视图，光标按最长公共前缀/后缀映射回原位）。
- **改文本 → 积木** 在你切回块视图时重建（每敲一个键就重建块，画布会抖到没法用）。

AST 在 `src/lang/` 里，是**纯 TypeScript** —— 不依赖 Electron / Node / Blockly，所以解析器、打印器、块转换器都能在纯 Node 里跑单测。IDE 自己的词法（73 个 token 种类）和语法（57 个节点种类）照着编译器仓库的 `compiler/src0/` 写。

**积木表达不了的语法不会静默消失。** 泛型、turbofish、闭包、指针、借用、切片、`defer`、`asm!`、属性 —— 这些落进一个**不透明块**，里面装着原始源码文本。挪它、删它都行；只要**你**不动它，那部分代码逐字节往返无损。

还有一条：**裁判永远是真实编译器**。IDE 从不猜程序对不对，它去跑 `jhyy.exe`，解析它的 `file:line:col: error: …` 输出，把编译器自己的诊断显示给你。仓库 README 记的一次「检查」约 185ms（用 `--no-link` 跳过链接）。

## 积木和文本从不同时占屏

块画布满整个编辑区，代码编辑器整个消失 —— 用标题栏的积木按钮、`Ctrl+Shift+B` 或命令面板切过去。切换时两边都**保留状态**：画布的缩放和平移留着，编辑器的撤销历史和光标位置也留着。

## 底部面板：问题 + 终端

- **问题** —— 编译器的诊断，点一条直接跳到那一行那一列。
- **终端** —— 一个真 shell（默认 MSYS2 的 bash，PowerShell 和 `cmd` 也能切），能开多个。终端优先走**真 PTY**（node-pty / Windows ConPTY）；node-pty 装不上时退到管道，这时 `vim`、`top` 这类全屏 TUI 跑不了 —— 而且退的时候状态栏会显示徽章，不静默变假。「运行」跑在你**正在看的那个终端**里，跑完终端还活着，提示符回来。

> README 里记的还是「问题 / 输出 / 终端」三个页签。**「输出」页签已经在开发中的版本里删掉了** —— 编译器和程序的输出现在都进终端，跟 VS Code 一个路子。

## 快捷键

菜单栏、命令面板、快捷键是**同一张命令表**的三种看法（`src/renderer/commands/registry.ts`），所以菜单里标出来的快捷键一定就是真能按的那个。

- `Ctrl+Shift+P` —— 命令面板
- `Ctrl+Shift+B` —— 切换块视图 / 文本视图
- `Ctrl+Shift+D` —— 检查
- `F5` / `Shift+F5` —— 运行 / 停止
- `Ctrl+J` —— 显示/隐藏底部面板
- `Ctrl+Shift+M` —— 问题
- 终端 —— `Ctrl` 加反引号；新建终端 —— `Ctrl+Shift+Backquote`
- `Ctrl+Alt+B` —— 显示/隐藏聊天侧栏；`Ctrl+Alt+I` —— 聚焦聊天
- `Ctrl+S` / `Ctrl+O` / `Ctrl+Shift+S` —— 保存 / 打开 / 另存为
- `Ctrl+,` —— 设置

## 一致性门：{{ide_gate_pass}}/{{ide_gate_total}}

IDE 的解析器和打印器必须跟**真实编译器**说同样的话。这靠编译器仓库自己的示例程序来保证 —— 语料是编译器仓的 `compiler/tests/examples/`（会随编译器一起长）；去掉没有入口函数的库文件、带 `SKIP` / `XFAIL` 指令的、以及以 `_` 开头（环境相关 / 需手工准备）的那些，进 gate 的是 **{{ide_gate_pass}}** 个 —— 这是 IDE 仓 CI 的全量口径。

两道门：

1. IDE 解析 → IDE 打印 → **真实 `jhyy.exe`** 编译（用 `--no-link`，跳过链接）；
2. 再**真跑一遍**，跟源码里的 `// EXPECT:` 指令比对。

语料口径跟语言仓库自己的规则一致：**以 `_` 开头的文件不进语料** —— 那批是环境相关 / 需手工准备的复现件。全量 {{ide_gate_pass}} 个要跑约 25 分钟，默认只跑一个代表性子集。

## 版本现状（这里有个不一致，如实说）

- `package.json` 写的是 **{{ide_version}}**；
- 仓库 README 顶部的**徽章还写着 v0.1.0** —— 徽章没跟上；
- 本地 `release/` 目录里留着的安装包也还是 **0.1.0** 那一份（是构建残留，不是发布渠道）。

GitHub Releases 上 **v0.1.0、v0.2.0、v{{ide_version}} 都已发布**，每个带一个 NSIS 安装包和一份 `SHA256.txt`。所以：**已发布的是 v{{ide_version}}**；而 `CHANGELOG.md` 顶部还有一节「未发布」（终端大改、设置对话框等），**源码树已经领先于任何一个已发布版本**。

要装，去仓库的 [Releases 页](https://github.com/JiHuiYiYou/JiHuiYiYou-IDE/releases)。

## 平台与前置条件

- **Windows x64** —— 目前只构建和验证了这一个平台；Linux / macOS 未构建。
- **Node.js 20+**（开发用的是 24）。
- **一个 JHYY 编译器** —— IDE **不含**编译器，每次编译、每条诊断都由真实的 `jhyy.exe` 出。它按这个顺序自动找：IDE 设置里配的路径 → 环境变量 `JHY_EXE` → `../JiHuiYiYou/compiler/build/bin/jhyy.exe`（仓库旁边那个开发构建）→ `C:\Program Files\JHYY\bin\jhyy.exe`（官方安装版）→ `PATH` 上的 `jhyy.exe`。

安装包**没有代码签名**，Windows SmartScreen 会拦一下，选「更多信息 → 仍要运行」。

## 文档

- **[Wiki](https://github.com/JiHuiYiYou/JiHuiYiYou-IDE/wiki)** —— 长文版指南：快速上手、架构、块子集、Claude Code、疑难排查、怎么加一个新块、怎么贡献（中英双语，7 个页面）。
- [`docs/blocks-subset.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-IDE/blob/main/docs/blocks-subset.md) —— 哪些语法有块，哪些没有，为什么。
- 仓库：<https://github.com/JiHuiYiYou/JiHuiYiYou-IDE>（MIT 协议）
