---
title: 治理
description: 谁决定、如何提议、如何发版——以及哪些地方还没有成文规则
layout: docs
project: compiler
zone: governance
---

# 治理

这一页回答三个问题：谁说了算、一次改动怎么被提出来、一个版本怎么发出去。
最后一节列出**目前还没有成文规则的部分**——那些条目宁可写「没有」，也不写成一句
听起来很成熟的话。

本页每一条规则都指向仓内的一个具体文件。找不到出处的，进最后一节的缺口表。

---

## 决策方式

JHYY 是**由个人维护的 pre-1.0 编译器项目**。这是仓库自己在 `SECURITY.md`
开头写的一句话，不是本站的修辞。

| 决定什么 | 谁拍板 | 出处 |
|---|---|---|
| 缺陷修复、诊断文案、构建脚本、工具链、文档 | 维护者本人 | `CONTRIBUTING.md` 的 PR 流程 |
| 语言语法 / ABI / 内存模型 / 标准库稳定 API / 错误码语义 / 自举边界 | 维护者本人，但**必须先有一份书面提案** | 这六项正是 `docs/abis/` 三份契约锁定的范围 |
| 版本号与发版时机 | 维护者本人 | 仓库根 `VERSION` 文件 + `scripts/dev/bump_version.py` |

仓库里唯一成文的「提案体例」是 `docs/plans/v4/<version>-plan.md`——一格一个版本槽，
统一结构：Context（为什么是这一版）· Goal（可度量）· Scope（范围）· 验收门 ·
启动时复核清单 · Critical files · Risks · Out of scope · References。
每份 plan 开头都写明「版本号是预留号，启动时按实际状态复核」。

跨项目的设计基线另有一处：`docs/coordination/`，编译器侧与 OS 侧各一份「终版」。

---

## RFC

**仓库里目前没有 RFC 目录，也没有 RFC 模板。** 核实过：`docs/` 下没有 `rfcs/`；
全仓 markdown 里出现的 "RFC" 只有两处，都是别的意思——Unicode 码点范围引
RFC 3629，installer GUID 生成引 RFC 4122。

所以下面两件事要分开讲：**哪些改动该走提案流程**（这条判断是清楚的）和
**提案该长什么样**（这条目前没有成文模板）。

### 哪些改动必须先有书面提案

| 改动 | 为什么 |
|---|---|
| 语言语法 | 规范 v{{spec_version}} 已锁版，语法是契约 |
| ABI（类型布局 / 调用约定 / struct 传参） | ABI v{{abi_version}} 已锁版，跨模块与跨目标都要对齐 |
| 内存模型 | 规范里的语义章节 |
| 标准库的稳定 API | 用户代码依赖它 |
| 错误码语义 | 诊断与退出码是用户可见契约 |
| 自举边界（哪些代码允许用 JHYY 写） | 决定编译器能不能继续编译自己 |

这六项对应的正是 `docs/abis/` 下三份文档覆盖的范围：语言规范、ABI、二进制格式。
它们是**锁定**的——锁版意味着改动要发一个契约版本，而不是蹭工具链的 patch 位。

### 哪些可以直接走 issue + 设计说明 + PR

缺陷修复、诊断信息、测试用例、构建与 CI 脚本、安装器与扩展、纯文档。
`.github/ISSUE_TEMPLATE/feature_request.yml` 的「Which area?」下拉里列着
Documentation / Tooling / Standard library / Target support——这些范围在仓库的
日常流程里没有提案这一环。改标准库的**新 API**属于上一张表；改一个既有函数的
行为细节属于这里。

### 提案该包含哪些部分

仓库里没有模板，下面是**约定草案**（不是现状）：

1. 动机——解决什么问题，不含方案
2. 设计目标
3. 非目标（明确不做什么）
4. 语法 / 语义草案
5. 类型与 IR 影响
6. ABI 与链接影响
7. arena 与裸机（freestanding）影响
8. 替代方案，以及为什么选这一条
9. 已知缺陷与局限
10. 迁移路径（对已有代码意味着什么）
11. 稳定性承诺（哪些行为从此不再变）
12. 实现阶段划分

### 打算怎么补

在仓内加 `docs/rfcs/` 目录与一份 `docs/rfcs/_template.md`，正文就是上面这十二项。
第一份提案从「语言规范 v4.1 的候选变更」开始写。

---

## Release

### 版本号怎么涨

**版本号的唯一真相源 = 仓库根的 `VERSION` 文件**，不手改。
当前稳定版与历史归档见[下载页](/compiler/download/index.html)。

刷一版有五个步骤，**顺序不能反**（`docs/internal/build.md` § 版本号自动化）。
下面命令里的版本号只是示例，实际按当时的排期定：

```bash
python scripts/dev/bump_version.py set 4.1.5   # 刷 VERSION + 全仓版本串 + 建 release note stub + 插 CHANGELOG 行
make                                           # 自举产物必须重编（版本号是 main.jhyy 里的字符串字面量）
pwsh -File installer/build.ps1 bundle          # 构建
python scripts/dev/bump_version.py finalize    # 回填 sha256 + 实测产物体积
python scripts/dev/bump_version.py check       # 零漂移门
```

第二步不能省：`make` 会把自举迭代到不动点，漏掉它，装出去的编译器会自报上一个版本号。

### 一个版本包含什么

一个 release = 一批改动落在某个版本槽上 + 一次 tag + 一次 GitHub Release +
三个产物（GUI 安装器 EXE / 企业分发 MSI / VS Code 扩展 VSIX）+ 一份
`installer/release-notes/<版本号>.md` 正文。

变更记录分两层，**这是仓内明写的约定**：

| 层 | 文件 | 规则 |
|---|---|---|
| 对外一行一条 | 仓库根 `CHANGELOG.md` | 一行一个版本；另有一张 release 表（有 tag）和一张 change slot 表（没有 tag） |
| 逐版本细节 | `docs/archive/logs/v4/changelog-v4.0.0.md` | **一条版本轴只有一个 umbrella changelog**，patch 版本往同一个文件里加一节，**不另开文件** |

v4 轴的 umbrella 里已经是 `## v4.0.1`、`## v4.0.2`、`## v4.1.4` 这样一节一节往下排。
IDE 仓的 `CHANGELOG.md` 开头写着同一条约定。

### 发版前要过的门

`release.yml` 里每道发布门都带一个 `# gate:` 标记：

| 门 | 查什么 |
|---|---|
| `release-version` | `VERSION` 文件与 tag 不符 ⇒ 拒发 |
| `release-ci-green` | 手动发布路径下，对应 tag 的 CI run 必须是 success |
| `release-anchor` | release 那次构建的产物与提交进仓的那份，对同一份源码产出的汇编逐字节相同 |
| `release-build` | Burn bundle + MSI + VSIX 构建成功 |
| `release-sha256` | `SHA256.txt` 与产物逐一对得上 |
| `release-notes` | 占位符没填 ⇒ 拒发；`installer/release-notes/<版本号>.md` 缺失 ⇒ 直接失败 |
| `release-msi` | `wix msi validate` |
| `release-artifacts` | 该有的产物一个不能少 |

在此之前，CI 侧还要过自举闭环、提交产物同步、全量回归、断言强度、产物级断言、
SysV ABI 跨实现对拍等门——清单在 `docs/internal/FACTS.md` § 2。

**强制点在 workflow 的 `needs:`，不在仓库设置。** tag 路径下 release job 依赖
`build-and-test + vscode-ext + sysv` 三道 job 全绿才启动；`main` 的 required status
check 是 GitHub 侧的仓库设置，而 `enforce_admins` 是关的——管理员可以绕过它。

### 没有三通道

仓库里**没有 nightly / beta / stable 三条发布通道**，也没有自动化的预发布构建。
只有两类东西：**已发布的 release**（有 tag、有 GitHub Release、有产物）和
**change slot**（在树里，但自己不带 tag 不带产物，内容随之后那一次发布一起出去）。

唯一的「预发布」形态是 RC：发布流程会把 RC 那个 tag 标成 GitHub 的 prerelease
——v4.0.0-rc1 就是这么发的。

下载页上标的 `stable` / `beta` 是**目标成熟度**（某个 target 三元组到哪一步了），
不是发布通道。

---

## 契约版本与工具链版本是两件事

| | 契约 | 工具链 |
|---|---|---|
| 是什么 | 语言规范 / ABI / 二进制格式 | 编译器 + 标准库 + 安装器 |
| 版本 | 语言规范 v{{spec_version}} · ABI v{{abi_version}} · 二进制格式 v{{binary_format_version}}（**设计稿，未实装**） | v{{site_version}}（{{site_version_date}}） |
| 什么时候变 | 改语义才动 | 缺陷修复天天动 |

语言规范 v{{spec_version}} 与 ABI v{{abi_version}} 是 v4 世代的契约基线，规范文档头部标注的锁版日是
**2026-10-24**——那一天 `jhyy-lang-spec-v1.3.0.md` 及其 17 份 v3.x supplement
一并归档进 git 历史，因为它们互相矛盾：v1.3.0 文档化过从未实装的块表达式，
也文档化过会静默算错的字面量。

**为什么这样切**：契约改一次，编译器、已经在写的用户代码、OS 线、IDE 的块语法
全都要跟着动。所以契约用独立的版本号，改契约发一个契约版本；工具链的 patch 位
只装不改变语义的东西。v4.1.4 修的那一批——第 16 个之后的实参被丢弃、SysV 栈实参
覆盖调用者的局部变量、浮点栈实参路径踩坏 callee-saved 的 `%xmm15`——全是实现缺陷，
不动语义，所以只涨 patch。

规范正文还有一条写法纪律：**只写当前代码确实已实装的行为**，未实装或受限的
统一收进附录 B。于是「契约页」写的是承诺，「工具链版本」写的是承诺兑现到哪一步
——两件事，两个版本号。

顺带一提：`v4.0.0 final` 从未 promote（当时问题台账没清零），v4 轴是从
`v4.0.0-rc1` 起的。

---

## 目前还没有成文规则

这一节是本页最该被读的部分。以下每一条都**核实过仓库现状**，不是推测。

| 缺什么 | 现状 | 打算怎么补 |
|---|---|---|
| RFC 目录与模板 | 仓库里没有 `docs/rfcs/`，也没有任何 RFC 模板 | 建目录 + 模板，正文见本页 RFC 一节 |
| RFC 评审人怎么定 | 没有任何规则写「谁审、几个人批、反对意见怎么裁决」 | 在 `docs/rfcs/README.md` 里定一条最简规则：触及三份契约的提案需要维护者书面同意 + 一名独立复核 |
| CODEOWNERS | **四个仓库都没有 CODEOWNERS 文件** | 按目录写一份：契约文档、问题台账、CI workflow 指到维护者，其余目录指向贡献者 |
| 发布负责人 | 没有第二个角色。`SECURITY.md` 自述「maintained by one person」 | 短期内维护者本人承担；等有第二个能独立跑通发版链的人，再写轮值规则 |
| 商标政策 | 仓库里**没有任何商标 / logo 使用政策文件** | 写 `TRADEMARK.md`：允许描述性用途，禁止暗示官方背书，禁止改 logo |
| 分支保护与合并规则 | 没有成文要求。`docs/internal/build.md` 记录了一个事实：`enforce_admins` 是关的，管理员可以绕过 `main` 的 required status check | 把「合并前自己跑门」写成文档级要求，并在 GitHub 侧打开 `enforce_admins` |
| 行为准则的跨仓库覆盖 | 编译器仓有 `CODE_OF_CONDUCT.md`；**IDE / OS / for-VEX 都没有** | 给后三个仓补，或明确写「以编译器仓那份为准」 |
| 安全披露的跨仓库覆盖 | 编译器仓与 IDE 仓有 `SECURITY.md`；**OS 仓与 for-VEX 仓没有** | 为后两个补最小版，或写明走编译器仓的私密通道 |
| for-VEX 的许可证 | **for-VEX 仓根目录没有 LICENSE 文件**——四个仓里唯一一个 | 补一份与其它三个相同的 MIT（`Copyright (c) 2026 JHYY`） |
| 贡献者协议（CLA / DCO） | 没有要求 | 暂不引入。若引入，先写清「引入之后历史 PR 怎么办」 |
| i18n 政策 | 没有 | 官网先单语（中文）；英文版等有人长期维护再开 |

**为什么把这些写出来**：小团队最容易出问题的不是「规则不够严」，而是「规则
指向一个不存在的人」。上面每一条补齐时，都要同时写清**谁负责**——否则过几个月
这条就过期了。宁可让社区页承认自己缺什么，也不要写出一个看起来完整、
实际没人执行的制度。

---

## 相关

- [许可证](/compiler/governance/license.html)——MIT 的确切条款与各仓许可现状
- [仓库地图](/compiler/governance/repo-map.html)——四个仓库各管什么
- [贡献指南](/compiler/community/contributing.html)——提 issue 与开 PR 的具体步骤
