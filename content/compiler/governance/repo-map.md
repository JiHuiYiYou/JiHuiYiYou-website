---
title: 仓库地图
description: 四个仓库各管什么，编译器仓库内部每个目录干什么
layout: docs
project: compiler
zone: governance
---

# 仓库地图

四个仓库，一件事一件分开。这一页先说四个仓库的边界，再逐个目录说明编译器仓库的
内部结构，最后给一张「我想改 X → 先读 Y」的对照表。

---

## 四个仓库的职责边界

| 仓库 | 干什么 | 当前状态 | GitHub | 相关文档在哪 |
|---|---|---|---|---|
| **Compiler** | 语言 + 编译器 + 标准库。编译器唯一实现在 `compiler/src0/`，后端是自研 amd64 发射器 | 稳定（自举成立，回归全绿） | [JiHuiYiYou-compiler](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler) | 仓内 `docs/`：`abis/` 三份契约、`internal/FACTS.md`、`plans/v4/` |
| **IDE** | 桌面工作台。Blockly 拖块与 CodeMirror 文本共用同一棵 AST，右侧栏接本机的 Claude Code | 测试中 | [JiHuiYiYou-IDE](https://github.com/JiHuiYiYou/JiHuiYiYou-IDE) | IDE 仓 `docs/wiki/*.zh-CN.md` |
| **OS** | 用 JHYY 写的操作系统。仓里目前只有引导 spike（`boot.s` + `BOOTX64.EFI` + `esp_root/` + `wrap_gpt.py`），原设计文档已随一次重整清空 | 孵化中 | [JiHuiYiYou-OS](https://github.com/JiHuiYiYou/JiHuiYiYou-OS) | 编译器仓 `docs/coordination/JHYY_OS侧设计终版.md` |
| **for-VEX** | VEX V5 Brain 嵌入式目标（Xilinx Zynq / Cortex-A9）。路线是 JHYY 直出 ARM 机器码，链官方 SDK 出 `.bin` | 孵化中（第 0 步实测阶段） | [JiHuiYiYou-for-VEX](https://github.com/JiHuiYiYou/JiHuiYiYou-for-VEX) | for-VEX 仓 `docs/00-事实基线.md`、`docs/第0步-验收线.md` |

四者之间只有两条耦合：**IDE 与 for-VEX 依赖编译器**；**OS 与编译器共享 ABI**
（所以跨项目设计基线放在编译器仓的 `docs/coordination/`，而不是各仓各一份）。

---

## 编译器仓库的目录地图

### 编译器本体

| 目录 | 管什么 |
|---|---|
| `compiler/src0/` | **编译器唯一实现**，`.jhyy` 源码。前端（`lexer` / `parser` / `ast` / `sema` / `types` / `symtab` / `mono` / `ir` / `ffi`）到后端（`codegen` / `codegen_amd64_*`）到 ABI 实现（`abi_amd64_*`）到 CLI（`main.jhyy`）都在这里。**仓里没有 C 端**（旧 `compiler/src/*.c` 已删除）⇒ 不存在「双实现 parity」这回事 |
| `compiler/src0/std/` | 用户侧标准库，**{{stdlib_modules}} 个模块**：`mem` `fmt` `io` `math` `string` `vec` `os` `arena`。模块名就是模块名，**没有 `std::` 前缀** |
| `compiler/src0/jhyy_helpers.c` | 编译器与 libc 之间的 C 桥。其中 4 个必需 FFI 符号只在 `#ifdef _WIN32` 内定义且没有 `#else` ⇒ **宿主只能是 Windows** |
| `compiler/src0/bootstrap/v1.0/` | 早期自举阶段的历史材料，不是当前路径 |
| `compiler/src0/scripts/dev/` | 源码树内的开发脚本 |
| `compiler/src0/main_run.s` | 生成的汇编产物，不是手写的 |

### 运行时

| 目录 | 管什么 |
|---|---|
| `compiler/runtime/` | **C 支撑运行时**：`runtime.c`（用户程序链接时链进去的那一份）+ `runtime.h`。`no_std_core/` 是 `#[no_std]` 时的替代实现（memcpy / memset / panic_handler / `__start_kernel`，全是 `.jhyy` 写的）——那种情况下 `runtime.c` **不参与链接** |
| `runtime/linux_elf/` | 仓库根的另一个 `runtime`：**`amd64_sysv_freestanding` 目标的静态无 libc Linux ELF64 运行时**（`crt0.S` + `link.ld`）。跟 `compiler/runtime/` 不是一回事，名字撞了而已 |

### 测试与产物

| 目录 | 管什么 |
|---|---|
| `compiler/tests/examples/` | 回归用例源（`.jhyy`），下划线开头的是辅助 fixture 不是用例 |
| `compiler/tests/golden/` | AST 黄金文件（`*.ast.txt`） |
| `compiler/tests/bootstrap/` | 自举与交叉验证脚本：`closure_check.sh`（跨代闭环）、`fixed_point.sh`（跨代不动点）、`byte_equal.sh`、`artifact_checks.sh`（产物级断言）、`artifact_fresh_check.sh`（提交产物 vs 现编产物）、`sysv_*.sh`（SysV ABI 门）、`bench.sh`、`mutation_test.py` |
| `compiler/build/` | 构建产物：`bin/`（`jhyy.exe` 是**git 跟踪的自举锚点**）、`obj/`、`regalloc/`。改了 `src0` 不提交新二进制，CI 的 `artifact-fresh` 门会红 |
| `regress.py` | 仓库根的回归驱动 |
| `Makefile` | 仓库根。`make` = 编 C 桥 + 自举闭环迭代到不动点 |

### 文档

| 目录 | 管什么 |
|---|---|
| `docs/abis/` | **三份契约**：语言规范 v{{spec_version}}（锁定）、ABI v{{abi_version}}（锁定）、二进制格式 v{{binary_format_version}}（**设计稿，未实装**） |
| `docs/internal/` | 内部文档：`FACTS.md`（事实单一真相源）、`workarounds.md`（问题台账，**永不归档**）、`architecture.md`、`build.md`、`feedback-codes.md`、`README.md`（文档索引） |
| `docs/archive/` | 历史归档：`logs/`（各轴 changelog + sprint 日志）、`plans/`（各轴 sprint 计划）、`perf/`（已被取代的性能测量）、`audit/`（codegen 深审 + RCA）。**归档不改** —— 它描述的是当时的世界 |
| `docs/plans/v4/` | 当前计划线，一格一个版本槽一份 `vX.Y.Z-plan.md` |
| `docs/coordination/` | 跨项目设计基线（编译器侧 / OS 侧各一份终版） |
| `docs/perf/` | 现行性能基线（帧尺寸 / 访存占比 / 回归比） |

### 工具与分发

| 目录 | 管什么 |
|---|---|
| `vscode-ext/` | VS Code 扩展 `jhyy-lang`：TextMate 语法高亮 + 原生 run / compile 命令 + 终端 profile 探测。`jhyy-lang-*.vsix` 是已构建产物 |
| `mcp-jhyy/` | Claude Code 的 MCP 服务（编译 / 运行 / 看 IL / 查台账 / 跑回归），Python 实现，门 `mcp-pytest` |
| `installer/` | Windows 装机：WiX（Burn bundle EXE + MSI）+ 内置 ucrt64 工具链 + `release-notes/`（每版 release note 正文）+ `distribution/`（scoop / winget manifest）+ `GUIDS.md`（安装器 GUID 登记） |
| `scripts/dev/` | 门脚本与开发工具：`bump_version.py`（版本自动化）、`check_arch_claims.py`、`check_spec_consistency.py`、`check_binary_format_layout.py`、`check_regalloc_parity.py`、`docs_facts_check.py`、`audit_test_assertions.py`、`check_regress_facts.py`、`test_docs_gate_mutations.py`、`bench/runtime_perf.py`、`regalloc_reference.py` |
| `bench/` | 基准套件：`tasks/`（题目）、`bench.py`（驱动）、`difftest.py`（随机程序差分）、`METHODOLOGY.md`（口径）、`seeds/`、`baseline/` |

仓库根还有几个文件各管一件事：`VERSION`（版本号唯一真相源）、`CHANGELOG.md`、
`CONTRIBUTING.md`、`SECURITY.md`、`CODE_OF_CONDUCT.md`。

---

## 我想改 X，先读 Y

| 我想改… | 先读 | 再读 |
|---|---|---|
| 语言语法或语义 | `docs/abis/jhyy-lang-spec-v4.0.0.md`（正文 + 附录 B） | `compiler/src0/parser.jhyy` / `sema.jhyy`；契约变更走提案 |
| FFI、struct 传参、调用约定 | `docs/abis/jhyy-abi-v4.0.0.md` | `compiler/src0/abi_amd64_*.jhyy` |
| 后端（codegen / 发射） | `docs/internal/architecture.md` | `compiler/src0/codegen_amd64_*.jhyy`；动 `src0` ⇒ 发版级流程 |
| 诊断信息、报错文案 | `docs/internal/workarounds.md`（先查是不是已知问题） | `compiler/src0/lexer.jhyy` / `sema.jhyy` |
| 标准库 | `compiler/src0/std/*.jhyy`（真实 API 在这里，不在文档里） | `docs/internal/workarounds.md`；改稳定 API 走提案 |
| 构建、工具链、门 | `docs/internal/build.md` | `Makefile`、`scripts/dev/`、`.github/workflows/` |
| 二进制格式 `.jhyynb` | `docs/abis/jhyy-binary-format-v1.0.0.md`（**设计稿，未实装**） | `scripts/dev/check_binary_format_layout.py` |
| 安装器与分发 | `installer/README.md` | `installer/build.ps1`、`installer/wix/`、`installer/distribution/` |
| VS Code 扩展 | `vscode-ext/README.md` | `vscode-ext/src/`、`syntaxes/` |
| MCP 服务 | `mcp-jhyy/README.md` | `mcp-jhyy/server.py` |
| 基准与口径 | `bench/METHODOLOGY.md` | `bench/tasks/`、`bench/bench.py` |
| OS 相关设计 | `docs/coordination/JHYY_OS侧设计终版.md` | `docs/coordination/JHYY_编译器侧设计终版.md` |
| 引用一个「会变的数字」 | `docs/internal/FACTS.md` | —（别在别处复述，复制即漂移） |
| 想知道「这行代码当初为什么这么写」 | `docs/archive/`（按轴查 changelog 与 RCA） | — |

---

## 相关

- [编译器实现](/compiler/docs/compiler.html)——流水线与后端怎么走
- [构建与测试](/compiler/docs/build-and-test.html)——怎么把它跑起来
- [贡献指南](/compiler/community/contributing.html)——提 issue 与开 PR 的步骤
- [许可证](/compiler/governance/license.html)——各仓的许可现状
