# JHYY 家族官网 — 设计文档

> 描述**已经建成**的站：四个项目（编译器 / IDE / OS / for-VEX）的官网枢纽，
> 编译器区是完整的五区 MVP。
>
> 本文档讲「是什么 / 为什么 / 怎么改」；视觉 tokens 就是 `assets/css/main.css`
> 与 `assets/css/docs.css` 里的 `:root` 变量本身。

---

## 0. 文档分工

**一条规则只写一处；别处只留指针。**

| 文档 | 只管什么 | 不许写什么 |
|---|---|---|
| **`DESIGN.md`（本文）** | 站点结构、视觉与内容决策、决策记录、现状与待办 | 逐页写作细则（→ `tools/CONTENT_GUIDE.md`）、命令清单（→ `README.md`） |
| `tools/CONTENT_GUIDE.md` | 写 `content/**` 的规约：front matter、Markdown 方言、文风、事实来源 | 设计决策、构建命令 |
| `README.md` | 仓库门面：这是什么、怎么构建、命令、目录 | 设计细节、写作细则 |
| `assets/fonts/README.md` | 字体资产清单与许可 | 设计理由（→ §9） |

**不另起分册。** 待办、阶段划分、进度一律留在本文 §10 —— 不新建
`Task.md` / `TODO.md` / `PLAN.md`：分册的下场是同一件事写两遍，然后两份都漂。

---

## 1. 北极星

**进站 5 秒要传达的事：让一个不懂编译器的开发者也想往下看，看完想装。**

| 层级 | 目标 | 实现路径 |
|---|---|---|
| **视觉冲击** | "这站不是 AI 套壳" | 暗黑主调 + 青绿强调色 + 大字符句（拉丁走 Instrument Serif，中文走系统无衬线） |
| **继续阅读** | "这内容值得看完" | swimlane 节奏（一屏一主题），不堆叠，每个 section 都有"具体可说的事" |
| **内容质量** | "看完想装" | 准确、有细节、不空泛；数字 / 案例 / 可操作的 CTA |

**反北极星（要避开的）：**
- "Hello World"式 hero（"为 X 而生" + "为 Y 而设计"堆叠）
- AI-generic 三栏卡片 + 蓝紫渐变
- 首页重复编译器子站已经讲过的内容
- 没有 install 入口的"快来用"按钮

---

## 2. 设计总规则

### 2.1 双层切换原则

| 层级 | 调性 | 字体 | 配色 |
|---|---|---|---|
| 门脸层 | **炫、有戏、可看** | Serif 大字 + 代码穿插 | 深黑底 + 青绿 accents |
| 文档层 | **克制、密、可学** | Sans 为主 + Mono 代码 | 近白底 + 深灰文本 |

两层切换时要有"视觉门"的过渡：从门脸点「文档」落到白底文档页，
靠的是**版式的整体换血**（深色玻璃胶囊导航 → 浅色三栏顶栏），不是动效。

### 2.2 微动效原则（Stripe 哲学）

**每个动效都有功能目的，不为炫而炫：**
- 入场 fade-up（reveal）：传达"模块就位"
- 代码 typewriter：传达"程序在跑"
- hover transform（150-200ms）：操作反馈
- 永远不要：循环闪烁、悬浮跳出来、强视差

时长预算：单次动效不超过 600ms，绝大部分 200-400ms。

**「减少动态效果」是硬要求，不是可选项。** `prefers-reduced-motion: reduce`
命中时：碎片、雾气物理、打字机、磁吸**全部停**，只留入场 reveal 与 hover
反馈（reveal 直接显形，不做位移）。这一条同时约束 CSS 与 JS —— 只在 CSS 里
写 `@media` 不够，打字机与物理效果是 JS 驱动的。

**原生光标保留。** 之前全站 `cursor: none`，换来的是没有文本 I 形光标、
没有可预期的指针、键盘用户也看不出焦点在哪。`.cursor-dot` 保留为**拖影装饰**
（更小、更淡、不响应 hover 放大），不是指针的替身。

### 2.3 组件复用规则

门脸层和文档层**绝不复用同一组件**：
- 文档层的卡片 / 列表 / 导航组件，全部按"信息密集、安静"设计
- 门脸层的卡片 / 列表 / 章节组件，按"视觉强、可玩"设计
- 共享的只有 atoms：图标 / 代码块 / 链接

---

## 3. 信息架构

### 3.1 路由

```
/                                  家族首页（四个项目）
/compiler/                         编译器首页（门脸层）
/compiler/docs/                    文档区（浅色三栏）
  /compiler/docs/getting-started.html
  /compiler/docs/tour.html
  /compiler/docs/reference.html
  /compiler/docs/spec.html
  /compiler/docs/abi.html
  /compiler/docs/stdlib.html
  /compiler/docs/arena.html
  /compiler/docs/osdev.html
  /compiler/docs/cli.html
  /compiler/docs/compiler.html
  /compiler/docs/build-and-test.html
  /compiler/docs/faq.html
/compiler/download/                下载区（浅色三栏）
  /targets.html  /bootstrap.html  /verify.html
/compiler/community/               社区区（浅色三栏）
  /conduct.html  /contributing.html  /security.html
/compiler/governance/              治理区（浅色三栏）
  /license.html  /repo-map.html
/ide/  /os/  /vex/                 另外三个项目的落地页（门脸层）
```

### 3.2 家族结构

```
                       ┌─ /          （枢纽：四项目分流）
                       │
   进来 ── 看完 ──────►├─ /compiler/ （编译器：完整五区）
                       │
                       ├─ /ide/  /os/  /vex/   （各自一页 + 仓库文档外链）
                       │
                       └─ /compiler/community/  （怎么参与）
```

**三个早项目的分栏不指向站内空页**，直接链各自仓库里的真实文档——
不为凑导航栏造一个没有内容的站内页面。

---

## 4. 门脸层设计（深 + 青绿 + 大字）

### 4.1 Hero

- 大字符句标语 + 一句话定位 + 双 CTA
- 品牌标记（`<img>`，自托管 SVG）
- **版本闸门**（`.version-gate`）：紧贴 hero 下沿，显示编译器版本、发布日、
  语言规范与 ABI 的契约版本、宿主平台

**hero 不放代码窗口。** 首页是**枢纽**，讲的是「这门语言 + 四个项目」；
可运行的代码样例是编译器子站（`/compiler/` 的「03 / A taste of the language」）
的职责，放在首页就是重复。首页给的是**版本闸门**——读者第一眼要知道的是
「现在能装的是哪个版本」，不是「这段代码长什么样」。

### 4.2 四个项目（家族首页）

大 Bento：编译器 `--lg`（span 7，跨两行），IDE `--sm`，OS `--sm`，VEX `--wide`
—— 这套 span 正好填满 12 栏（7+5=12，OS 落在第二行右侧，VEX 整行）。

每张卡四件套：**定位一句话 + 现在到哪一步 + 一个数字 + 一个 CTA**。
只写**现在真的做到哪一步**，不含计划中的部分。成熟度用视觉区分
（`data-status`：编译器实心主卡，其余描边卡）。

### 4.3 一门语言撑起四个项目（关系图）

一张图讲清家族结构 —— 这是**首页独有的内容**，任何子站都讲不了：

```
共享层：语言规范 · ABI · 自研后端 · 标准库
              │
          编译器
        ╱    │    ╲
      IDE  for-VEX  OS
```

三个分支各写一句「**它要编译器额外给什么**」——
IDE 要「同一个 `jhyy.exe` 出诊断」，for-VEX 要「ARM 后端」，
OS 要「freestanding 目标 + 裸机能力」。

### 4.4 最近变化 + 诚实的边界

左栏是这一版修了什么（取自编译器仓 `CHANGELOG.md`），
右栏是**没做什么** —— 安装器与 MSI **未签名**、只有 **amd64** 四个 target、
**UEFI 入口路径未完工**、基准比值是**代码质量下限**而非快慢达标线。

这些必须写在页面上，不能藏进脚注。

> 改版前的首页有第五屏「五个高频出口」（下载 / 文档 / 标准库 / 源码仓库 /
> 社区规则）。**删掉了** —— 同样的五个去处在顶栏、页脚、项目切换器里
> 各出现一次，占一整屏只为重列一遍导航。

---

## 5. 文档层设计（白底 + 干净 + 信息密度）

### 5.1 Layout

三栏（参考 learn.microsoft.com）：

```
┌─────────────────────────────────────────────────┐
│ 顶栏：项目切换 / 五区导航 / 搜索 / 版本 / GitHub  │
├───────┬─────────────────────────────┬───────────┤
│  左   │   中：内容主区                │  右       │
│  TOC  │   - h1 / h2 / h3             │ On this   │
│  可折 │   - 段落 + 列表 + 代码        │ page      │
│  叠   │   - Callout(note/warn/danger) │ anchor    │
└───────┴─────────────────────────────┴───────────┘
```

- 顶栏：固定，搜索按钮按 `/` 唤起
- 左 TOC：sticky，按区（docs / download / community / governance）切换内容
- 中内容：`max-width: 760px`
- 右 anchor：sticky，滚动时高亮当前小节

### 5.2 内容骨架

```
content/
├─ index.html                     家族首页（门脸）
├─ compiler/
│  ├─ index.html                  编译器首页（门脸）
│  ├─ docs/*.md                   12 页文档
│  ├─ download/*.md               4 页下载
│  ├─ community/*.md              4 页社区
│  └─ governance/*.md             3 页治理
├─ ide/index.md  os/index.md  vex/index.md
└─ en/                            **英文树** —— 与上面同构
   ├─ index.html
   ├─ compiler/index.html + docs/ download/ community/ governance/
   └─ ide/index.md  os/index.md  vex/index.md
```

`en/` 下的每个文件都有中文孪生页（`route` 相同即孪生）：
`content/en/compiler/docs/tour.md` ↔ `content/compiler/docs/tour.md`。
孪生关系由 `tools/i18n.py` 的 route 契约管，`tools/check_twins.py` 守。

### 5.3 关键页面规格

- **教程页**：左 TOC + 中 markdown + 代码块（语法高亮、复制按钮）
- **参考页**：表格密、可跳转 ID 链接
- **搜索**：顶栏 `/` 唤起，客户端索引（`search-index.json` 由构建器生成）

### 5.4 调性

- 文字优先，图形极少（最多代码块）
- 字体：Inter 正文、JetBrains Mono 代码
- 配色：近白底 (`#fbfbfa`) + 深灰文本 (`#16161a`) + 青绿强调 (`#007a66`)
- **不动效**（除滚动进度）

---

## 6. 内容流水线

```
content/**/*.md     ──┐
content/**/*.html   ──┤
                      ├─→ tools/build.py ──→ *.html（提交进仓库，GH Pages 直出）
tools/siteconfig.py ──┘         │
tools/i18n.py ──────────────────┤
                                ├─→ search-index.json
                                └─→ tools/build.py --check（链接与锚点检查）
```

- `tools/siteconfig.py` —— **全站唯一真相源**：版本号、目标表、产物表、
  状态数字、导航与侧栏、以及 `FACTS`（事实占位符的取值表）。
- `tools/i18n.py` —— 术语表（`GLOSSARY`）、界面字符串（`UI`）、专名白名单
  （`KEEP_CJK`）、孪生页契约（`TWIN_REQUIRED` / `TWIN_EXEMPT_PREFIXES`）。
- `tools/mdrender.py` —— 零依赖 Markdown 渲染器（CommonMark 子集 +
  callout + mermaid + `[[Wiki 链接]]`）。
- `tools/build.py` —— 站点生成器 + 链接检查 + **双语双树**。
- `tools/check_examples.py` —— 把文档里的 `.jhyy` 代码块抽出来交给真编译器验。
- `tools/CONTENT_GUIDE.md` —— 内容写作规约（文风 / 方言 / 事实来源 / 常见坑）。

**门**（本地可跑，CI 也跑）：

| 门 | 查什么 | 级别 |
|---|---|---|
| `tools/check_facts.py` | `siteconfig.FACTS` ↔ 编译器仓 `docs/internal/FACTS.md` 对拍（17 项） | 错误 |
| `tools/check_twins.py` | 每个页面都要有中英两版 | 错误 |
| `tools/check_i18n.py` | 正文里不许手写事实（改用 `{{key}}`）、英文页里不许出现中文、术语说法一致 | 错误 + 警告 |
| `tools/build.py --check` | 站内链接与锚点不断（两棵树都扫） | 错误 |
| 同步门（CI 里 `git diff` + `git ls-files --others`） | `content/` 改了要重建；**未跟踪的生成物也算** | 错误 |

**事实只有一份。** 正文里写 `{{site_version}}` / `{{regress_pass}}` 这类占位符，
构建器从 `siteconfig.FACTS` 取值 —— **两种语言拿的是同一份常量，不可能对不上
数字**。`check_facts.py` 负责跟编译器仓那份真相对拍（之前官网写着「回归 279
PASS」，编译器仓已经改成 281 了，没有任何门会红）。

**约定：正文用根绝对路径写站内链接**（`/compiler/docs/tour.html`），
构建时按页面深度自动改写成相对路径——站点挂在 `user.github.io/<repo>/`
下也不会 404。

---

## 7. 组件清单

### Atoms（门脸 + 文档复用）
- `Icon`：内联 SVG
- `CodeBlock`：语言标识 / 复制按钮
- `Link`：内 / 外链接区分样式

### 门脸层专属
`Hero`（大字 + CTA + 版本闸门）· `Bento` · `Card` · `ToolCard` ·
`PerfCell` · `EcoCard` · `DocCard` · `VersionGate` · `CTA` ·
`FamilyGraph`（共享层 → 编译器 → 三分支）· `ChangeGrid`（最近变化 / 诚实的边界）

### 文档层专属
`DocTopbar`（含项目切换与搜索）· `TOC` · `OnThisPage` · `Callout`
（note / warn / danger）· `RefTable` · `SearchModal`

### 两层共用（只有 atoms）
`Icon`（内联 SVG）· `CodeBlock`（语言标识 / 复制按钮）· `Link` ·
**`LangSwitch`**（语言切换，普通 `<a>`，无 JS 依赖）

---

## 8. 反模式（明确禁止）

- ❌ Tailwind 默认 `bg-blue-500` 类配色
- ❌ "Fast ⚡ Simple ✨ Powerful 💪" AI-generic 卖点
- ❌ Hero 区贴一张"团队微笑"或者办公室的 stock photo
- ❌ 文档层加 scroll-reveal 动效（除 progress indicator）
- ❌ 用 emoji 当 UI 元素
- ❌ **编造数字**——每个断言都要能追溯到一个文件
- ❌ **藏起已知缺口**——未签名、UEFI 未完工、基准比值的口径都要写在页面上
- ❌ 用 `curl | bash` 式的信任盲区（校验步骤要能被复现）
- ❌ **正文里手写事实**（版本号、回归数、门数）—— 用 `{{key}}` 占位符，
  否则中英两棵树迟早对不上，而且没人会红
- ❌ **英文页里出现中文**（专名白名单 `KEEP_CJK` 除外）—— 一页一种语言，
  不混排
- ❌ **一屏只为重列一遍导航**（顶栏 / 页脚 / 项目切换器里已有的去处）

---

## 9. 决策记录

| 项 | 决定 | 理由 |
|---|---|---|
| 框架 | **纯静态 + 自写 Python 生成器** | 原决策是 Next.js + Vercel，但仓库里从未落地 Next.js（没有 `package.json`）。实际建成的是静态 HTML + 手写 CSS + GH Pages。改版报告 §8 同样建议「Markdown 长文 + 编译器生成 API + 数据驱动下载页」而不是押注单一重型框架。 |
| 样式 | 手写 CSS（`main.css` 门脸 / `docs.css` 文档） | 两套调性差异大，手写比抽象层便宜 |
| 部署 | GitHub Pages（仓库根） | 纯静态产物，无需构建服务 |
| 下载分发 | 站点镜像 + GitHub Releases 双通道 | 镜像字节与线上发行件**逐字节一致**（已用 GitHub API 的 digest 核对），所以两边 SHA256 都能验过 |
| 搜索 | 客户端索引（`search-index.json`） | 规模还小，先不上服务端 |
| 代码高亮 | 手写 CSS（无第三方高亮库） | 减少依赖；门脸层的代码块本来就带自定义 span 标记 |
| i18n | **构建期双树**：`content/**` 中文（`/`）+ `content/en/**` 英文（`/en/`） | 报告说 i18n 是独立流水线、不阻塞一期；但站点当时是**语言沙拉**（编译器落地页英文、其余 28 页中文）。构建期双树让语言状态变成构建的一部分，而不是各页各自为政。现有中文 URL 不变。 |
| 事实 | **只有一份**，正文写 `{{key}}` 占位符 | 抄数字必然漂 —— 编译器仓把回归数从 279 改成 281 之后，官网还写着 279，而没有任何门会红。现在两边共用 `siteconfig.FACTS`，`check_facts.py` 跟编译器仓对拍。 |
| 字体 | **自托管**（`assets/fonts/`，latin + latin-ext 子集） | `fonts.googleapis.com` 在中国大陆取不到，取不到就整站掉回系统默认字体。中文走系统 CJK 栈 —— 那四款字体本来就没有汉字字形。资产清单与许可见 `assets/fonts/README.md`。 |
| 展示字族 | 拉丁 Instrument Serif + 中文系统无衬线 | Windows 只带宋体，大字下横竖粗细差太大、发旧；思源宋体多数机器没装（自托管子集要 100+ 切片、3 MB 起，不值）。 |
| 强调色 | **只有青绿一套** | 之前品牌青绿之外还混着琥珀（卡片 hover 会闪金色）、紫（雾气）、红（logo 辉光）—— 一页四套强调色。logo 自身的紫蓝渐变是 logo 的颜色，不算 UI 强调色。 |
| 不引入 | 后端、数据库、admin、Playground | Playground 是安全与维护黑洞，报告点名说它不是一期必做 |

---

## 10. 现状与待办

**已完成**：四项目枢纽、编译器五区 24 页、站内搜索、链接检查、
文档示例真编译验证、下载镜像与校验和同步到 v4.1.4；
**首页重做**（纯枢纽四屏：Hero / 四个项目 / 一门语言撑起四个项目 / 最近变化与诚实的边界）；
**双语地基**（构建期双树、语言切换器、术语表、事实占位符）+ 5 页门脸中英双版；
**四道新门**（事实对拍 / 孪生页 / i18n 一致性 / 同步门补未跟踪产物）。

**下一步**（i18n 的第二阶段）：
- 文档层 24 页的英文版 —— 译完就把 `i18n.TWIN_EXEMPT_PREFIXES` 那四行删掉，
  孪生页门自动覆盖全站
- IDE / OS / VEX 三个门脸的**结构**重做（它们现在仍是 Markdown 墙）
- 编译器落地页 12 屏的结构重做（本轮只做了翻译与编号修正）

**二期候选**（按报告 §10 的门槛判定）：
- 版本化文档（`stable / nightly / archive`）与 `noindex`
- 错误码索引（把 `W-NNN` 与诊断号做成可搜索符号）
- Playground（只在「安装/首次编译」确实是流失点时才上）

**已知缺口**（写在这里，也写在官网治理页里）：
- 四个仓库都没有 `CODEOWNERS`
- 编译器仓没有 RFC 目录与模板
- 编译器仓没有商标政策
- winget 包 `JiHuiYiYou.JHYY` 的 manifest 在仓库里，但**上游 `microsoft/winget-pkgs` 未合并**
- `#[no_std]` 的链接分支依赖相对 CWD 的 side-file，异地构建会回落失败
- `#[naked]` 函数在 `.s` 里没有标签，裸中断入口目前不可用
- 标准库 `arena_reset` 的可用窗口按 `def_size` 算但实际块更小 ⇒ 特定尺寸区间越界
