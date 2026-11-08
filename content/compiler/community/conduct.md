---
title: 行为准则
description: 参与这个项目的最低约定
layout: docs
project: compiler
zone: community
---

# 行为准则

这一页是仓库里 [`CODE_OF_CONDUCT.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/CODE_OF_CONDUCT.md) 的**导读**，不是它的副本。原文是英文的、条款式的；这里把它重写成能一眼读完的版本，遇到分歧以原文为准。

适用范围：仓库、issue、PR、review、discussion、wiki、release，以及**代表本项目在公开场合发言**的时候。

---

## 核心约定

这四条是从原文里抽出来的实际要求：

**1. 尊重 + 善意推定。**
默认对方是在帮忙，哪怕效果是错的。

**2. 区分「作品错了」和「人错了」。**
给出并接受有建设性的技术反馈。这是编译器项目，几乎所有分歧都在于作品本身。

**3. 分歧要有实质。**
给理由、给证据、说清楚**什么能改变你的想法**。这是原文明确写的技术讨论标准——「这个设计是错的」永远没问题，「我要赢这个论辩」不是。

**4. 报问题要精确具体。**
原文的判断是：模糊的报告花掉维护者的时间比省下的多。

另外两条原文也写明的：把责任担起来、向受影响的人道歉并从错误里学；把重点放在对项目和使用者更好上，而不是赢一场争论。

---

## 不可接受的行为

原文列得很短，这里照实列：

- 性化的语言或图像，以及任何形式的性关注或性追求。
- 挑衅、侮辱或贬损的言论，人身攻击或政治攻击。
- 公开或私下的骚扰。
- 未经明确许可，公开他人的私人信息——例如住址或邮箱。
- 在专业场合中其他被认为不恰当的行为。

> [!NOTE]
> 这不是一份「社区宣言」。它是一份**最低约定**：上面五条就是全部，没有更多隐藏条款。

---

## 怎么举报

| 渠道 | 用途 |
|---|---|
| 邮件 **15901598712@163.com** | 首选。写清发生了什么、在哪里发生（issue / PR / 群聊）、你希望怎么处理 |
| [私有 advisory](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/security/advisories/new) | 与安全报告共用同一条私密通道；只有你和维护者看得见 |

维护者有义务**保护举报人的隐私与安全**。

### 处置阶梯

原文给的是四级，由维护者按情况选用：

1. **Correction**——私下的书面警告，说明行为性质与为什么不当；也可以要求公开道歉。
2. **Warning**——警告并说明继续的后果，包括一段不与相关人员互动的时期。
3. **Temporary ban**——暂时禁止任何形式的互动或公开交流。
4. **Permanent ban**——永久禁止在本项目内的任何公开互动。

---

## 维护者的回应承诺

**已写明的**：所有举报会被「及时且公正地复核与调查」（原文：reviewed and investigated promptly and fairly），举报人隐私受保护。

**目前还没有明文规定的**：

- 处理时限。原文用的是定性措辞，**没有给出具体天数**。这和[安全披露](/compiler/community/security.html)那一页不同——那一页有明确的 7 天 / 14 天目标。行为准则这边目前没有对应数字，我们正在补。
- 举报结果是否回告举报人、以什么形式回告。
- 是否设立第二个人（仲裁人 / 委员会）来处理针对维护者本人的举报。

---

## 单维护者的局限（原文明说了）

这个项目**只有一个维护者**，所以执行行为准则的人，就是被要求处理举报的人——如果举报对象恰好是维护者本人。

原文没有回避这一点，官网也不回避。原文给出的出路是：走 GitHub 自己的[滥用举报渠道](https://support.github.com/contact/report-abuse)，或者不再继续往来。

我们把这条摆在这里，是因为把它藏起来只会在真正需要的时候伤害举报人。

---

## 与上游标准的关系

仓库的 `CODE_OF_CONDUCT.md` **改编自 [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct.html) 2.1 版**，处置阶梯的思路来自 [Mozilla 的 code of conduct enforcement ladder](https://github.com/mozilla/diversity)。

这是**改编**，不是逐字采用。逐条对下来有两处实质差别和一处小差别：

| | Contributor Covenant 2.1 | 仓库原文 |
|---|---|---|
| **Enforcement Responsibilities** 一节（社区负责人有义务澄清标准、删改不合规内容、说明处理理由） | 有 | **没有**——从 Scope 直接跳到 Enforcement |
| 技术分歧专段 | 没有 | **有**——一整段讲「分歧要给理由、给证据、说清什么能改变你的想法」 |
| 「有助于社区的行为」清单 | 5 条 | 同样 5 条，但第 1 条多了「善意推定」，第 5 条**新增**了「报告问题要精确具体」 |

另外一处小差别：「Our pledge」那段，CC 2.1 列举了 `caste` 与 `color`，仓库原文没有这两项。

两边不一致时，以仓库原文为准。

---

## 接下来

- [贡献指南](/compiler/community/contributing.html) —— 提 issue 与 PR 的具体路径。
- [安全披露](/compiler/community/security.html) —— 安全问题走私密通道，与这里分开。
- 原文：[`CODE_OF_CONDUCT.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/CODE_OF_CONDUCT.md)
