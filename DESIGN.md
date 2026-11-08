# JHYY 家族官网 — 设计文档

> 描述**已经建成**的站：四个项目（编译器 / IDE / OS / for-VEX）的官网枢纽，
> 编译器区是完整的五区 MVP。
>
> 本文档讲「是什么 / 为什么 / 怎么改」；视觉 tokens 就是 `assets/css/main.css`
> 与 `assets/css/docs.css` 里的 `:root` 变量本身。

---

## 1. 北极星

**进站 5 秒要传达的事：让一个不懂编译器的开发者也想往下看，看完想装。**

| 层级 | 目标 | 实现路径 |
|---|---|---|
| **视觉冲击** | "这站不是 AI 套壳" | 暗黑主调 + 青绿强调色 + serif 大字符句 + 一行可运行代码嵌入 hero |
| **继续阅读** | "这内容值得看完" | swimlane 节奏（一屏一主题），不堆叠，每个 section 都有"具体可说的事" |
| **内容质量** | "看完想装" | 准确、有细节、不空泛；数字 / 案例 / 可操作的 CTA |

**反北极星（要避开的）：**
- "Hello World"式 hero（"为 X 而生" + "为 Y 而设计"堆叠）
- AI-generic 三栏卡片 + 蓝紫渐变
- 没有可运行代码的"语言介绍"页
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
- 嵌入式代码块（语法高亮，typewriter 动效）
- **版本闸门**（`.version-gate`）：首屏下方固定显示编译器版本、发布日、
  语言规范与 ABI 的契约版本、宿主平台——首页的第一职责是「版本闸门」

### 4.2 四个项目（家族首页）

大 Bento：编译器 `--lg`（span 7，跨两行），IDE `--sm`，OS `--sm`，VEX `--wide`。
每张卡只写**现在真的做到哪一步**，不含计划中的部分。

### 4.3 编译器三张领域卡

新手 / OS 开发者 / 研究者三条主线各一张卡，每张导向站内具体文档，
不是营销口号。

### 4.4 五个高频出口

下载、文档、标准库 API、源码仓库、社区规则——每个都指向一个具体动作。

### 4.5 版本闸门与诚实条款

安装器与 MSI **未签名**、UEFI 入口路径**未完工**、基准比值是**代码质量下限**
而非快慢达标线——这些必须写在页面上，不能藏进脚注。

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
```

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
content/**/*.md  ──┐
                   ├─→ tools/build.py ──→ *.html（提交进仓库，GH Pages 直出）
tools/siteconfig.py ┘         │
                             ├─→ search-index.json
                             └─→ tools/build.py --check（链接与锚点检查）
```

- `tools/siteconfig.py` —— **全站唯一真相源**：版本号、目标表、产物表、
  状态数字、导航与侧栏。改版本号只改这一处。
- `tools/mdrender.py` —— 零依赖 Markdown 渲染器（CommonMark 子集 +
  callout + mermaid + `[[Wiki 链接]]`）。
- `tools/build.py` —— 站点生成器 + 链接检查。
- `tools/check_examples.py` —— 把文档里的 `.jhyy` 代码块抽出来交给真编译器验。
- `tools/CONTENT_GUIDE.md` —— 内容写作规约（文风 / 方言 / 事实来源 / 常见坑）。

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
`Hero`（大字 + CTA + 代码 + 版本闸门）· `Bento` · `Card` · `ToolCard` ·
`PerfCell` · `EcoCard`（五出口）· `DocCard` · `VersionGate` · `CTA`

### 文档层专属
`DocTopbar`（含项目切换与搜索）· `TOC` · `OnThisPage` · `Callout`
（note / warn / danger）· `RefTable` · `SearchModal`

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
| i18n | 官网单语（中文） | 报告：i18n 是独立流水线，不是一期阻塞项 |
| 不引入 | 后端、数据库、admin、Playground | Playground 是安全与维护黑洞，报告点名说它不是一期必做 |

---

## 10. 现状与待办

**已完成**：四项目枢纽、编译器五区 24 页、站内搜索、链接检查、
文档示例真编译验证、下载镜像与校验和同步到 v4.1.4。

**二期候选**（按报告 §10 的门槛判定）：
- 版本化文档（`stable / nightly / archive`）与 `noindex`
- i18n（社区翻译仓 → 站点原生）
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
