---
title: 贡献指南
description: 从提 issue 到 PR 合并的完整路径
layout: docs
project: compiler
zone: community
---

# 贡献指南

这一页是仓库 [`CONTRIBUTING.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/CONTRIBUTING.md) 的完整路径版：提 issue、跑门、写 PR。**动手前先确认你改的东西落在哪一档**。

---

## 仓库地图（简短版）

| 你要改的东西 | 在哪 |
|---|---|
| 编译器源码 + C 桥 | `compiler/src0/`（31 个 `.jhyy` 模块 + `jhyy_helpers.c`）——**唯一的实现**，没有第二份 |
| 后端 | `compiler/src0/codegen_amd64_*.jhyy`（自研 amd64 发射器） |
| 标准库 | `compiler/src0/std/`（8 个模块：`mem` / `fmt` / `io` / `math` / `string` / `vec` / `os` / `arena`） |
| 测试 | `compiler/tests/examples/` + 仓库根的 `regress.py` |
| 自举与门脚本 | `compiler/tests/bootstrap/` |
| 语言 / ABI / 二进制格式契约 | `docs/abis/` |
| 问题台账 | `docs/internal/workarounds.md`（**永不归档**，条目只关不删） |
| 会变的数字 | `docs/internal/FACTS.md`（**唯一真相源**） |
| 计划线 | `docs/plans/v4/`（一格一份 plan） |
| 跨项目设计基线 | `docs/coordination/`（编译器侧与 OS 侧各一份终版） |

完整版见[仓库地图](/compiler/governance/repo-map.html)。

---

## 构建与测试

宿主是 **Windows 10 + MSYS2**（`C:\msys64\mingw64\bin\bash.exe`）。

```bash
# 依赖
pacman -S --needed mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-binutils

# 构建（jhyy 编译自己；make 会把自举闭环迭代到不动点）
make all           # → compiler/build/bin/jhyy.exe

# 回归
python regress.py                       # 全量
python regress.py --tests=hello.jhyy    # 单个用例
python regress.py --all                 # 带上受门控的用例
```

> [!IMPORTANT]
> **不要**用 Git Bash 自带的那个 MinGW `gcc`——它不支持 PE+ 链接，会在链接阶段失败。
> **所有门都要从仓库根目录跑**：脚本按当前目录解析路径，在子目录里跑会把所有文件报成缺失，看起来像漂移，其实不是。

### 各道门分别管什么

| 门 | 它管什么 | 什么时候跑 |
|---|---|---|
| `make`（自举闭环） | 跨代产出的 `.s` **逐字节相同** | 改了 `compiler/src0/*.jhyy` 之后 |
| `python regress.py` | 每个用例的退出码 / stdout 断言 | 任何行为改动之后 |
| `python scripts/dev/audit_test_assertions.py --strict` | 每个用例都有**能失败**的断言（零信号即红）+ 指令与读点对照 | 改测试之后 |
| `bash compiler/tests/bootstrap/artifact_checks.sh` | 19 道**产物级**断言——失效模式在字节布局里，不在程序返回值里，写 `.jhyy` 测试抓不到 | 动了 codegen 之后 |
| `bash compiler/tests/bootstrap/closure_check.sh` | Stage 2 的 `.s` == Stage 3 的 `.s`（**本地门**，不接 CI） | 改了 `src0` 之后 |
| `python regress.py --fixed-point` | N=10 跨代 `.il` + `.s` 逐字节相同（**本地门**） | 发版级流程 |
| `bash compiler/tests/bootstrap/artifact_fresh_check.sh` | 提交进仓的那份 `jhyy.exe` 与现编产物行为一致 | 改了 `src0` 之后——否则它会红 |
| `python scripts/dev/bump_version.py check` | `VERSION` == 全仓每一处版本串 | 动了版本号或版本串 |

### 提交前该跑哪个

| 你改了什么 | 至少要跑 |
|---|---|
| 只改文档 / 只改测试 | 文档要事实核对（限制还在吗？修它的 sprint 发布了吗？），CI 跑事实门；测试要 `python regress.py` + 断言强度审计 |
| 改了 `compiler/src0/*.jhyy` | `make` + `python regress.py` + `artifact_checks.sh`，并更新提交进仓的自举产物；动版本号或发版流程再加 `--fixed-point` |

细节见[构建与测试](/compiler/docs/build-and-test.html)与[源码构建与自举](/compiler/download/bootstrap.html)。

---

## 改动分类与对应门槛

### 这几类必须先设计、后动手

**语言语法 / 语义 · ABI 与内存布局 · 内存模型 · 标准库稳定 API · 错误码语义 · 自举边界。**

理由：语言规范 v4.0.0 与 ABI 白皮书 v4.0.0 都是**已锁定**的契约，附录 B 是已知限制的正式清单，诊断码也在规范里成表——一动就影响所有已发布的程序。

> [!NOTE]
> **目前还没有明文规定的 RFC 流程。** 仓库里没有 RFC 模板、编号规则或评审期——`RFC` 这个词在仓内只出现在两个互联网标准里（RFC 3629、RFC 4122）。现有的替代物是：锁定中的规范 + 附录 B、`docs/plans/v4/` 一格一份 plan（结构固定，含 Goal / Scope / 验收门 / 复核清单 / Risks）、以及 `FACTS.md` § 4 这份排期真相源。官网的 [RFC 流程](/compiler/governance/index.html#rfc) 一节是这块规则正在补的位置。
>
> **在规则补齐之前的实际做法**：先开一个 issue 说明动机、范围、对现有代码的影响，等维护者拍板再动手；不要直接改规范文本。落在 `docs/plans/v4/` 哪一格、验收门是什么，写在 plan 里。

### 小改动

issue（说明问题）+ 设计说明 + PR，**设计说明自包含在 PR 里**——不要让 reviewer 自己去翻 issue。

---

## 提交与 PR 规范

以下四条是 `CONTRIBUTING.md` 的原文要求：

1. **一个 PR 只做一件事。** 描述里需要出现「并且」的时候，它大概是两个 PR。
2. **门必须跑。** **没跑过的门等于没过的门。** PR 上每个 CI job 都得绿——包括 **SysV ABI** 那道 job：它是唯一能真正**执行**那六个用例的 runner（`windows-latest` 会跳过它们），所以它绿了不代表覆盖了它们。
3. **提交信息里总结这次改动**；**任何 AI 助手参与了代码编写，都要加 `Co-Authored-By` trailer**。
4. **动了文档就把事实保持同步**。

### 改编译器源码 = 发版级流程

改 `compiler/src0/*.jhyy` 的成本比改文档高得多：**加一个局部变量就会移位模块级 temp 编号**，自举构建随之漂移。于是要：

- 跑全量回归；
- 刷新自举锚点（`make`，它会迭代到不动点并装上新二进制）；
- **提交新的 `compiler/build/bin/jhyy.exe`**——它是 git 跟踪的产物，CI 的 `artifact-fresh` 门会拿它跟现编产物对拍，陈旧的会被抓出来。

**只改注释是免费的**：lexer 在 codegen 之前把注释剥掉，编译器二进制保持逐字节相同。

### 代码风格

- `.editorconfig`：UTF-8 / LF / 末尾换行 / 去尾空格；缩进 **4 空格**（`.jhyy` / `.c` / `.h` / `.py` / `.sh` / `.ps1`）、**2 空格**（`.md` / `.json` / `.yml`），**Makefile 用 tab**。
- C 侧 `-Wall -Wextra` **零警告**。
- **一份文档一种语言**：对外门面（`README.md` / `CONTRIBUTING.md` / `CHANGELOG.md`）英文，中文门面只有 `README.zh-CN.md`，仓内 `docs/**` 中文；同一份文档里不许中英混写。中文只用简体。
- **两份 README 必须一起改**——门面分叉比门面过期更糟。
- 文档里的路径引用按「相对当前文件」写；改完跑 `python scripts/dev/docs_facts_check.py`（含断链检查）。

### 测试分层

回归套件共 299 条，按**信号来源**分三层：

| 层 | 判定方式 | 条数 |
|---|---|---|
| 真断言 | 断言写在用例源码里 | 215 |
| harness 判定 · 期望编译错误 | 用例声明 `// EXPECT-ERROR: "..."` | 56 |
| harness 判定 · 比对退出码 | 用例声明 `// EXPECT: N` | 8 |
| SKIP · 用例主动跳过 | 用例带 `// SKIP:` 指令 | 6 |
| SKIP · 库模块 | 没有入口点的库模块 | 14 |

215 + 56 + 8 = **279**（可跑），加 6 + 14 = **299**（总数）。

测试指令集是固定的一组：`EXPECT` / `EXPECT-ERROR` / `EXPECT-OUT` / `XFAIL` / `SKIP` / `SETENV`，新增用例只用这几个。

断言强度审计会报出**零信号用例数**——一个不可能失败的测试比没有测试更糟，它什么都没查却报成功。

### 签名要求与反向移植

- **签名要求：没有。** 仓库没有 DCO、没有 GPG 签名要求，GitHub 侧的 `web_commit_signoff_required` 也是关的。
- **反向移植（backport）规则：目前还没有明文规定。** 仓库只有一条主线（`main`），没有 release 分支矩阵，也没有 backport 政策。

---

## 两类贡献模板

> [!NOTE]
> **这两张表还没写进仓内的 `CONTRIBUTING.md`**——原文只规定了 PR 流程与门。表里的要求是项目现行的做法，先在官网发布成模板，写回仓内文档正在补。

### 教学贡献（教程 / 讲义 / 示例）

| 必附 | 说明 |
|---|---|
| **可运行的完整 `.jhyy` 文件** | 不是片段，不能省略 import 与 `main_jhyy` |
| **预期输出** | stdout **与**退出码，两者都要 |

放得进 `compiler/tests/examples/` 的示例最好——那样它同时是教学材料，也是回归用例。

> [!NOTE]
> **目前还没有明文规定的「教学材料目录」。** 仓库里没有 `docs/tutorials/` 之类的位置，长文目前放 Wiki。「教学材料必须带可运行示例」是从回归套件的既有纪律推出来的，不是成文条款——我们正在补。

### 编译器贡献

| 必附 | 说明 |
|---|---|
| **IR 示例** | `JHY_WRITE_IL=1` 出的 `.il`，让 reviewer 能看中间表示而不是猜 |
| **回归测试** | 新增 `.jhyy` 用例进 `compiler/tests/examples/`；修 bug 的话，**先写能复现的用例** |
| **性能 / 正确性影响** | 帧尺寸、访存、指令数这些静态指标，以及「有没有可能改变已有行为」 |

改了 `compiler/src0/*.jhyy` 还要额外声明**这是发版级改动**——PR 模板里有一项专门问这个。

---

## 提 issue 的格式

两个 issue 模板（*Compiler bug report* / *Feature request*），也允许空白 issue。报 bug 时这四样缺一不可：

1. **最小复现**——完整的 `.jhyy` 源码；
2. **实际 vs 预期输出**，**含退出码**；
3. **版本**——`jhyy --help` 的第一行（**没有 `jhyy --version` 这个 flag**，它从来没存在过）；
4. **编译器来源**——发布二进制，还是自举构建？

> [!WARNING]
> **退出码要用 harness 或 Python `subprocess` 取，不要读 MSYS2 bash 的 `$?`。** bash 把退出码截成 8 位（`value & 0xFF`），所以 ≥ 256 的期望码要先约减：827 → 59、501 → 245、300 → 44、1000 → 232。很多「退出码不对」的报告其实只是这个。

---

## issue 标签体系

仓库里**实际存在**的标签是下面这十三个：

| 标签 | 含义 | 来源 |
|---|---|---|
| `bug` | 编译器做错了 | *Compiler bug report* 模板默认 |
| `enhancement` | 功能请求 | *Feature request* 模板默认 |
| `documentation` | 文档改动 | 手工 |
| `question` | 提问 | 手工 |
| `good first issue` | 适合新人 | 手工 |
| `help wanted` | 需要额外关注 | 手工 |
| `duplicate` | 重复 | GitHub 默认 |
| `invalid` | 不成立 | GitHub 默认 |
| `wontfix` | 不会做 | GitHub 默认 |
| `roadmap` | 已排进路线图 | 手工 |
| `短期` / `中期` / `长期` | 排期档位 | 手工，对应 `FACTS.md` § 4 的时间轴 |

> [!NOTE]
> **目前还没有 `RFC`、`OS`、`backend`、`arena`、`breaking`、`needs-decision` 这些标签**——它们不存在于仓库。计划中的分域标签体系正在补。
> 另外两点现状：`good first issue` 标签存在，但当前**没有挂着它的开放任务**（开放 issue 数为 0）；Discussions 侧**没有单独的标签体系**。

---

## 接下来

- [社区首页](/compiler/community/index.html) —— 渠道与当前数字。
- [行为准则](/compiler/community/conduct.html) —— 参与这个项目的最低约定。
- [安全披露](/compiler/community/security.html) —— 不要把安全问题发到公开 issue。
- 原文：[`CONTRIBUTING.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/CONTRIBUTING.md)
