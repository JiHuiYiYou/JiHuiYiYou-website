# JHYY 家族官网 — 待办

> 这里只装**还没做的事**：要做什么、归属、做完怎么算过。
> 已经建成什么样、为什么这么设计 ⇒ [`DESIGN.md`](DESIGN.md)；
> 写页面时的规约 ⇒ [`tools/CONTENT_GUIDE.md`](tools/CONTENT_GUIDE.md)。
> **本文不描述现状，也不重复设计理由** —— 同一件事只写一处。
>
> 顺序用相对次序，不写日期估时。

---

## 下一轮

**队列：把三个仓的事实接进门。**

上一轮的四项都已完成：

- 三个项目页（IDE / OS / for-VEX）的门脸结构重做 —— 已完成（中英同构）；
- 编译器落地页 12 屏按「一屏一主题」收一遍 —— 已完成；
- 文档层 24 页的英文版 —— 已完成，**每个 route 都双语**（route 数记在
  `siteconfig.FACTS["site_routes"]`，孪生页门守着），
  `i18n.TWIN_EXEMPT_PREFIXES` 已清空；
- 仓库 `README.md` 改英文 + `README.zh-CN.md` —— 已完成。

**背景：**事实门只对拍**编译器仓**的 `FACTS.md`；IDE / OS / for-VEX 的事实
（`ide_version` / `ide_gate_*` / `os_spike_measured` / `vex_baseline_*`）
**不在任何门里** ⇒ 官网落后只能靠人记。**已经漂了三次**：

| 什么时候 | 官网写的 | 仓里实际的 |
|---|---|---|
| 前两轮 | 「消息泵 tick 频率待测」 | for-VEX 已在真 Brain 测得 100 Hz |
| 前一轮 | 「Day 1–2 一个都还没开始」 | Day 1–2 的第一个闭环已通 |
| 本轮 | 「B 路还是目标」 | B 路探针已走通（`routebvex.bin` 2580 B） |

⇒ **一次漂移就是官网在说假话。** 这条链要补上。

### 要做什么

1. **三个仓各出一份机器可读的事实**（跟编译器仓 `docs/internal/FACTS.md`
   同构、同一套键名）：IDE（版本 / 一致性门总数 / 门数）、OS（spike 行数 /
   已实测几件事）、for-VEX（八项基线 / Day 进度 / 产物大小）。
   —— **归属**：三个仓各自的维护者（跨仓待办，本仓只负责发起与对拍）。
2. **官网 `tools/check_facts.py` 扩展到对拍这三个仓**：本地按相对路径找，
   CI 里加三次 `actions/checkout`（三个仓都是公开的）；对拍项数从 17 变多。
3. **做完就把下面「常备 § 2」那条人工核对删掉** —— 它存在的理由就是没有门。

### 顺带（本站工程缺口，同批做）

- **`deploy` job 没把示例真编译挂进 `needs`** ⇒ 那道门红了站点照样上线
  （workflow 自己的注释说「守六件事」，实际上第六件拦不住部署）；
- **没有 `sitemap.xml` / `robots.txt` / `404.html`** ⇒ 对外站点缺基本的
  搜索入口与兜底页。

---

## 编译器每次发版后要做的事（常备）

> 事实门（`tools/check_facts.py`）会在编译器仓发版后**当场变红** —— 它比编译器仓
> 的 main 慢一步的那一次，就是官网还没跟上的证据。

### 1. 刷版本、镜像产物、改掉「已修却仍写成缺口」的表述

- **要做什么**（每次发版照这个单子走）：
  1. `tools/siteconfig.py` 的 `SITE_VERSION` / `SITE_VERSION_DATE` ——
     事实门会直接报出差哪两条；回归数、台账数走 `FACTS`（改一处即可）；
  2. 把三件产物镜像到 `downloads/`，`SHA256SUMS.txt` 与线上 `SHA256.txt`
     **逐字节相同**（用 GitHub API 的 digest 对拍，别只信文件名）；
  3. 首页与编译器落地页的「最近变化」改成新版本那一条；
  4. **把新版本修好的限制从文档层改掉** —— 别再把已修的东西写成缺口
     （v4.1.5 之前，官网把 `#[naked]` 的标签落位、`arena_reset` 的越界、
     `#[no_std]` 的 side-file 路径三处**已修**的东西当成现存限制在讲）；
  5. 仓库 `README.md` 里的版本串。
- **归属**：官网仓。
- **判据**：`python tools/check_facts.py` 全绿；三个产物的 sha256 与
  GitHub Releases 的 digest 一致；全仓搜旧版本号只剩**历史事实**与占位符。
- **顺带**：版本耦合的位置（下载页的文件名与 URL、校验页的命令、参考页的版本句）
  已改成 `{{site_version}}` 占位符 ⇒ 下次发版这几页不用再动。

### 2. 跨仓发版后：人工核 IDE / OS / for-VEX 的事实（**没有门对拍**）

- **要做什么**：事实门只对拍**编译器仓**的 `FACTS.md`；`ide_version` /
  `ide_gate_*` / `os_spike_measured` / `vex_baseline_*` 这几条来自**另外三个仓**，
  编译器仓的 `FACTS.md` 里没有 ⇒ **它们不会自动变红**。
  三个仓各自发版 / 补测之后，人工核一遍：
  1. IDE 仓：`package.json` 的 version、一致性门的 `277/277`；
  2. OS 仓：`spike/boot.s` 头注释里「实测到的几件事」；
  3. for-VEX 仓：`docs/00-事实基线.md` 的八项结论与实机观测（§ 13.1）。
- **归属**：官网仓（人工同步）。
- **判据**：三条都对回各自仓的原文；官网正文里没有「已测却写成待测」、
  也没有「待测却写成已测」。
- **为什么手写**：这三个仓的事实还没进任何门 ⇒ 只能靠人。**等它们进
  `FACTS.md` 的对拍范围，这一项就能删。**

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
