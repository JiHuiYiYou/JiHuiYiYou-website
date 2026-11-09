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

## 编译器每次发版后要做的事（常备）

> 事实门（`tools/check_facts.py`）会在编译器仓发版后**当场变红** —— 它比编译器仓
> 的 main 慢一步的那一次，就是官网还没跟上的证据。

### 5. 刷版本、镜像产物、改掉「已修却仍写成缺口」的表述

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
