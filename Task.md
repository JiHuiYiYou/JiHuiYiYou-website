# JHYY 家族官网 — 待办

> 这里只装**还没做的事**：要做什么、归属、做完怎么算过。
> 已经建成什么样、为什么这么设计 ⇒ [`DESIGN.md`](DESIGN.md)；
> 写页面时的规约 ⇒ [`tools/CONTENT_GUIDE.md`](tools/CONTENT_GUIDE.md)。
> **本文不描述现状，也不重复设计理由** —— 同一件事只写一处。
>
> 顺序用相对次序，不写日期估时。

---

## 下一轮（i18n 第二阶段 + 门脸结构）

### 1. 文档层 24 页的英文版

- **要做什么**：`content/en/compiler/{docs,download,community,governance}/**` 逐页译；
  译完删掉 `tools/i18n.py` 的 `TWIN_EXEMPT_PREFIXES` 四行。
- **归属**：官网仓（`content/en/**`）。
- **判据**：`python tools/check_twins.py` 在豁免名单清空后仍全绿；
  `python tools/check_i18n.py` 无 CJK 报错；中英逐页字段对拍一致。

### 2. IDE / OS / VEX 三个门脸的结构重做

- **要做什么**：三页现在是 Markdown 墙，没有门脸版式 —— 按首页那套屏结构重做。
- **归属**：官网仓。
- **判据**：三页走门脸层版式（`layout: page`）而不是文档层三栏；
  1440 / 390 两个宽度人工过一遍截图。

### 3. 编译器落地页 12 屏的结构重做

- **要做什么**：上一轮只做了翻译与编号修正，屏序与信息密度没动。
- **归属**：官网仓（`content/compiler/index.html` + `content/en/compiler/index.html`）。
- **判据**：12 屏各有明确职责、不互相重复（按 `DESIGN.md` §3 的「一屏一主题」判据）。

### 4. 仓库 `README.md` 改英文 + 补 `README.zh-CN.md`

- **要做什么**：家族规约要求对外门面用英文，本仓 `README.md` 现在是中文。
- **归属**：官网仓。
- **判据**：`README.md` 全文英文；`README.zh-CN.md` 与之同步；
  两份是互译关系，不是互补关系。

---

## 等 v4.1.5 发布后（编译器仓在关的尾）

### 5. 刷版本号与状态数字

- **要做什么**：`tools/siteconfig.py` 的 `SITE_VERSION` / `SITE_VERSION_DATE`；
  回归数、台账数走 `FACTS`（改一处即可）。
- **归属**：官网仓（`tools/siteconfig.py`）。
- **判据**：`python tools/check_facts.py` 全绿 —— 它会**先红**，那正是它的用处。

### 6. 更新三条已修限制的表述

- **要做什么**：`content/compiler/docs/osdev.md` 仍写「`#[naked]` 的符号落位不对，
  裸中断入口不可用」（台账 W-223）、`content/compiler/docs/arena.md` 仍写
  「`arena_reset` 把 `end` 设成 `start + def_size`」（W-222）、`osdev.md` 里
  `#[no_std]` 侧文件那段的表述（W-124）—— 这三条在 v4.1.5 已 RESOLVED，
  站点跟着版本走 ⇒ 必须改成已修状态。
- **归属**：官网仓（`content/compiler/docs/**`）。
- **判据**：三条表述与编译器仓台账状态一致（台账是唯一真相源），
  数字全部走 `{{key}}` 占位符。

> 这三条是复核编译器仓 `docs/internal/workarounds.md` 时发现的：台账早已 RESOLVED，
> 官网仍当现存限制在讲。**结论：「缺口清单」这类会变的东西不能手抄进官网文档**，
> 每次对着台账核 —— 抄一次就开始漂。

---

## 二期候选（尚未启动）

| 候选 | 门槛 |
|---|---|
| 版本化文档（`stable / nightly / archive`）与 `noindex` | 要有 nightly 产物才值得做 |
| 错误码索引（把 `W-NNN` 与诊断号做成可搜索符号） | 要先把诊断号与台账号对齐 |
| Playground | 只在「安装 / 首次编译」确实是流失点时才上 |

---

## 跨仓待办（不在本仓做，列出以免丢）

| 事项 | 归属 | 出处 |
|---|---|---|
| 四个仓库都没有 `CODEOWNERS` | 四个仓的维护者 | 官网治理页缺口表 `content/compiler/governance/index.md` |
| 编译器仓没有 RFC 目录与模板 | 编译器仓 | 同上 |
| 编译器仓没有商标政策 | 编译器仓 | 同上 |
| winget 包上游 `microsoft/winget-pkgs` 未合并 | 上游合并请求 | 下载页 winget 一节的 WARNING（`content/compiler/download/index.md`） |

> 官网**不重复**这些缺口的细节：官网治理页是对外的说明面，
> 编译器仓 `docs/internal/workarounds.md` 是台账真相源，
> 官网的数字只从 `siteconfig.FACTS` 取。
