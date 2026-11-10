---
title: 社区
description: 去哪里问、怎么参与、当前的状态数字
layout: docs
project: compiler
zone: community
---

# 社区

这一页回答三件事：**问题往哪里问**、**不同类型的贡献分别怎么进来**、以及**这个项目此刻的数字是多少**。

先说清楚现状：这个项目由**一位维护者**主导，下面列的都是真实存在的渠道，不是设想的社区结构。渠道少，人也少——这是事实，不是谦辞。

---

## 去哪里问

| 你要做的事 | 去哪 | 说明 |
|---|---|---|
| 问「这个语言怎么写」 | [GitHub Discussions](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/discussions) | 分类是 GitHub 默认的六类：Announcements / General / Ideas / Q&A / Show and tell / Polls |
| 报「编译器做错了」 | [GitHub Issues](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/issues) → *Compiler bug report* | 模板要求最小复现、实际与预期输出、版本、退出码 |
| 提「我想要这个功能」 | 同上 → *Feature request* | 模板先问**你要解决的问题**，方案可以留空 |
| 提一个改动 | [Pull requests](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/pulls) | 走[贡献指南](/compiler/community/contributing.html) |
| 报安全问题 | **私有 advisory**，不要开公开 issue | 见[安全披露](/compiler/community/security.html) |
| 随便聊、问进度 | QQ 群 **429807125** | 搜群号加入 |
| 邮件 | **15901598712@163.com** | 行为准则举报与安全报告的兜底渠道 |

仓库另外开了 **Wiki**（放长文）与 **Projects**（项目看板）。Issues 也允许空白 issue——模板只是引导，不是门槛。

> [!NOTE]
> Discussions 频道已开通，但目前里面还没有帖子。这是一个刚起步的频道，第一个把问题讲清楚的人会替后面省很多事。

---

## 当前的状态数字

下面这些是**会变的数字**，唯一真相源在仓库的 `docs/internal/FACTS.md`；官网的副本在 `tools/siteconfig.py`。

| 指标 | 值 | 出处 |
|---|---|---|
| 自举闭环 | `make` 迭代到不动点，跨代产出的 `.s` **逐字节相同** | FACTS § 2 |
| 回归套件 | **{{regress_pass}} PASS / {{regress_failed}} FAIL / {{regress_skip}} SKIP**（共 {{regress_total}} 条） | FACTS § 2 |
| 断言强度 | {{assertions}} 条真断言，**零信号用例 0** | FACTS § 2 |
| 产物级门 | {{artifact_checks}} 道 | FACTS § 2 |
| 问题台账 | {{workarounds_total}} 条：**ACTIVE {{workarounds_active}}** / DEFERRED {{workarounds_deferred}} / RESOLVED {{workarounds_resolved}} / SUPERSEDED {{workarounds_superseded}} / INVALID {{workarounds_invalid}} | FACTS § 3 |
| 宿主平台 | **1 个**（Windows x64） | build.md |
| 目标三元组 | **4 个**（2 个 stable / 2 个 beta） | FACTS § 5 |
| 许可证 | MIT | 仓库根 `LICENSE` |

**这些数字各自的边界**，别读过头：

- 「跨代逐字节相同」证明的是**生成确定性**，不是语义正确性。一个确定性的错误编译器也能完美闭环——这是经典的 trusting trust 缺口，由回归套件那道门补上。
- 「ACTIVE 0」的意思是**没有已登记的**未修编译器 bug，不是「不存在 bug」的证明。台账是公开的，任何人都能查：[`docs/internal/workarounds.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/workarounds.md)。
- 「{{regress_pass}} PASS / {{regress_skip}} SKIP」里的 {{regress_skip}} 条 SKIP 是带 `// SKIP:` 指令的用例和无入口的库模块，不是「跑失败被跳过」。

---

## 怎么参与

四类贡献的入口和门槛不一样。先判断你手上的活属于哪一类，再看对应的要求。

### 编译器改动

入口：[贡献指南](/compiler/community/contributing.html)。门槛最高，也最值钱——因为编译器是自举的，改 `compiler/src0/*.jhyy` 会牵动自举锚点。**必附**：IR 示例（`JHY_WRITE_IL=1` 出的 `.il`）、新增回归用例、性能与正确性影响的说明。

### 文档

入口：同样是 PR。门槛：改动**仍然要事实核对**——那个限制还在吗？修掉它的那个 sprint 真的发布了吗？一份写错的文档比一份过期的文档更糟。仓库里所有会变的数字只在 `FACTS.md` 一处，其余文档引用它；文档改动还会被 CI 的事实门对拍。

### 教学材料

入口：教程、讲义、示例代码。门槛：**必须附可运行的完整 `.jhyy` 文件 + 预期输出（stdout 与退出码）**。示例最好是能直接进 `compiler/tests/examples/` 当回归用例的那种——那样它同时是教学材料，也是测试。

### OS 与裸机

入口：`docs/coordination/` 里的跨项目设计基线（编译器侧与 OS 侧各一份终版）是跨边界的唯一依据，改 OS 相关设计前先读它。门槛：裸机与内核开发路径见[裸机与内核开发](/compiler/docs/osdev.html)。

---

## 关于「社区」这件事的实话

截至 2026-11-08，仓库累计 **9 个 issue、8 个 PR，全部由维护者本人提交并已关闭**，当前开放 issue 数为 **0**，star 8、fork 0。

这不是在劝退。含义是：

- **提 issue 不会被淹掉**——没有排队等待的队列。
- **但也没有第二个人替你 review**。PR 的评审目前由维护者一人完成，反馈周期取决于他当天的状态，这一点我们不编一个假的 SLA 出来。
- 维护者对**安全问题**有明确的响应目标（见[安全披露](/compiler/community/security.html)）；对**普通 issue 和 PR**，目前没有明文规定的响应时限——这一条我们正在补。

参与这个项目最省力的方式，是先在 [Discussions](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/discussions) 里把问题问清楚，再决定要不要写成 PR。

---

## 接下来

- [贡献指南](/compiler/community/contributing.html) —— 从提 issue 到 PR 合并的完整路径。
- [行为准则](/compiler/community/conduct.html) —— 参与这个项目的最低约定。
- [安全披露](/compiler/community/security.html) —— 报告安全问题，以及已知的信任边界。
- [仓库地图](/compiler/governance/repo-map.html) —— 每个目录归谁管。
